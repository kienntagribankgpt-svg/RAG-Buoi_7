import re
import html
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_14")
kb_hops_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_10/graph_rag_labs/kb+hops")
output_file = base_dir / "data" / "processed" / "chunks_normalized.csv"

print("=" * 70)
print("PROMPT 1: CHUẨN HÓA CORPUS CHO RETRIEVAL & CITATION")
print("=" * 70)

df_content = pd.read_csv(kb_hops_dir / "content.csv")
df_meta = pd.read_csv(kb_hops_dir / "metadata.csv")

def clean_html(raw_html):
    if not isinstance(raw_html, str):
        return ""
    text = re.sub(r"<style[\s\S]*?</style>", "", raw_html)
    text = re.sub(r"<script[\s\S]*?</script>", "", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

df_merged = pd.merge(df_content, df_meta, on="id", how="left")

normalized_records = []
for _, row in df_merged.iterrows():
    doc_id = str(row["id"]).strip()
    title = str(row.get("title", doc_id)).strip()
    so_ky_hieu = str(row.get("so_ky_hieu", "")).strip()
    loai_vb = str(row.get("loai_van_ban", "")).strip()
    co_quan = str(row.get("co_quan_ban_hanh", "")).strip()
    
    cleaned_full_text = clean_html(row["content_html"])
    
    # Tách văn bản theo từng Điều khoản nếu có
    articles = re.split(r"(?=(?:Điều\s+\d+[\.:\s]))", cleaned_full_text, flags=re.IGNORECASE)
    
    if len(articles) <= 1:
        # Tách theo đoạn nếu không có từ khóa 'Điều x'
        articles = [p.strip() for p in cleaned_full_text.split("\n\n") if len(p.strip()) > 30]
        if not articles:
            articles = [cleaned_full_text]
            
    for idx, art_text in enumerate(articles):
        art_text = art_text.strip()
        if len(art_text) < 25:
            continue
        
        match_art = re.match(r"(Điều\s+\d+)", art_text, flags=re.IGNORECASE)
        art_name = match_art.group(1) if match_art else f"Phần {idx+1}"
        
        chunk_id = f"{doc_id}_art_{idx+1}"
        citation = f"[{title} | {so_ky_hieu} | {art_name} | {chunk_id}]"
        
        normalized_records.append({
            "chunk_id": chunk_id,
            "document_id": doc_id,
            "text": art_text,
            "title": title,
            "so_ky_hieu": so_ky_hieu,
            "loai_van_ban": loai_vb,
            "article": art_name,
            "citation": citation,
            "source_file": "content.csv"
        })

df_norm = pd.DataFrame(normalized_records)
df_norm.to_csv(output_file, index=False, encoding="utf-8")

print(f"✔ Đã chuẩn hóa thành công: {len(df_norm)} chunks từ {df_norm['document_id'].nunique()} văn bản.")
print(f"✔ File output: {output_file}\n")
for i, r in df_norm.head(2).iterrows():
    print(f"[{i+1}] {r['chunk_id']} -> Citation: {r['citation']}")
    print(f"    Text: {r['text'][:100]}...\n")