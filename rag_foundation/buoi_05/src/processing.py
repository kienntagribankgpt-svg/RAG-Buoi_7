import os
import re
import json
import argparse
import asyncio
import unicodedata
import pymupdf as fitz  # PyMuPDF via pymupdf package
from dotenv import load_dotenv
from llama_cloud import AsyncLlamaCloud

# Nạp API key từ file src/.env
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH)
LLAMA_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# 1. Chuẩn hóa Unicode NFC
def normalize_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)

# 2. Xử lý đọc PDF & Fallback OCR với LlamaParse
async def extract_pdf_text(pdf_path: str, output_dir: str):
    doc = fitz.open(pdf_path)
    full_text = ""
    ocr_used = False
    file_name = os.path.basename(pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        if not text.strip() or len(re.findall(r'[^\x00-\x7F\u00C0-\u1EF9\s]', text)) > 20:
            ocr_used = True
            break
        full_text += f"\n--- Trang {page_num + 1} ---\n" + text

    if ocr_used:
        print("[INFO] Text layer bị lỗi/rỗng. Đang chạy OCR bằng LlamaParse...")
        if not LLAMA_KEY:
            raise ValueError("Chưa tìm thấy LLAMA_CLOUD_API_KEY trong file src/.env!")

        client = AsyncLlamaCloud(api_key=LLAMA_KEY)
        file_obj = await client.files.create(file=pdf_path, purpose="parse")
        result = await client.parsing.parse(
            file_id=file_obj.id,
            tier="agentic",
            version="latest",
            expand=["markdown_full"],
        )
        full_text = result.markdown_full

    full_text = normalize_nfc(full_text)

    os.makedirs(output_dir, exist_ok=True)
    raw_path = os.path.join(output_dir, "raw_extracted.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    return full_text, ocr_used, file_name, len(doc)

# 3. Chiến lược Fixed-size Chunking
def fixed_size_chunking(text: str, source: str, total_pages: int, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        chunks.append({
            "chunk_id": f"fixed_{idx}",
            "strategy": "fixed-size",
            "source": source,
            "page_start": 1,
            "page_end": total_pages,
            "text": chunk_text,
            "length": len(chunk_text)
        })
        idx += 1
        start += (chunk_size - overlap)
    return chunks

# 4. Chiến lược Semantic Chunking
def semantic_chunking(text: str, source: str, total_pages: int):
    paragraphs = text.split("\n\n")
    chunks = []
    for idx, p in enumerate(paragraphs):
        p_clean = p.strip()
        if p_clean:
            chunks.append({
                "chunk_id": f"semantic_{idx}",
                "strategy": "semantic",
                "source": source,
                "page_start": 1,
                "page_end": total_pages,
                "text": p_clean,
                "length": len(p_clean)
            })
    return chunks

# 5. Chiến lược Hierarchical Chunking
def hierarchical_chunking(text: str, source: str, total_pages: int):
    pattern = r'(?=(Chương\s+[IVXLCDM\d]+|Điều\s+\d+|Mục\s+\d+))'
    splits = re.split(pattern, text)

    if len(splits) <= 1:
        print("[CẢNH BÁO] PDF không có cấu trúc Chương/Mục/Điều. Tự động chuyển về Semantic Chunking.")
        return semantic_chunking(text, source, total_pages)

    chunks = []
    idx = 0
    for i in range(1, len(splits), 2):
        header = splits[i]
        content = splits[i + 1] if (i + 1) < len(splits) else ""
        chunk_text = (header + content).strip()
        chunks.append({
            "chunk_id": f"hierarchical_{idx}",
            "strategy": "hierarchical",
            "source": source,
            "page_start": 1,
            "page_end": total_pages,
            "text": chunk_text,
            "metadata_cautruc": {"heading": header},
            "length": len(chunk_text)
        })
        idx += 1
    return chunks

# 6. Tính toán thống kê min, max, trung bình
def get_stats(chunks):
    if not chunks:
        return {"count": 0, "min_len": 0, "max_len": 0, "avg_len": 0}
    lengths = [c["length"] for c in chunks]
    return {
        "count": len(chunks),
        "min_len": min(lengths),
        "max_len": max(lengths),
        "avg_len": round(sum(lengths) / len(lengths), 2)
    }

# 7. Luồng chạy chính hỗ trợ dry-run và --write
async def main():
    parser = argparse.ArgumentParser(description="RAG Buổi 5 - OCR & Chunking Process")
    parser.add_argument("--write", action="store_true", help="Ghi kết quả ra thư mục output")
    args = parser.parse_args()

    pdf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "datademo", "van_ban_mau.pdf"))
    output_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output"))

    if not os.path.exists(pdf_path):
        print(f"Lỗi: Không tìm thấy file {pdf_path}")
        return

    text, ocr_used, source_file, total_pages = await extract_pdf_text(pdf_path, output_dir)

    fixed = fixed_size_chunking(text, source_file, total_pages)
    semantic = semantic_chunking(text, source_file, total_pages)
    hierarchical = hierarchical_chunking(text, source_file, total_pages)

    data = {
        "fixed": fixed,
        "semantic": semantic,
        "hierarchical": hierarchical
    }

    if args.write:
        os.makedirs(output_dir, exist_ok=True)
        out_json = os.path.join(output_dir, "chunks_result.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Đã ghi kết quả vào: {out_json}")
    else:
        print("[DRY-RUN MODE] Chạy thử nghiệm thành công (chưa ghi file JSON). Dùng cờ --write để xuất file.")

    print("\n" + "="*50)
    print(f"FILE: {source_file} | Đã dùng OCR: {ocr_used}")
    print("="*50)
    for name, chunks in [("Fixed-size", fixed), ("Semantic", semantic), ("Hierarchical", hierarchical)]:
        stats = get_stats(chunks)
        print(f"► {name:<12}: Số chunk = {stats['count']:<4} | Min = {stats['min_len']:<4} | Max = {stats['max_len']:<5} | Avg = {stats['avg_len']}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
