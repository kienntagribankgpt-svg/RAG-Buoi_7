import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from google import genai

# 1. Cấu hình kết nối Neo4j DB
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# 2. Khởi tạo Mô hình Embedding & Gemini API Client
print("Đang khởi tạo mô hình Embedding (CPU mode)...")
embed_model = SentenceTransformer("thuannc/vi-distilled-msmarco-MiniLM-L12-cos-v5", device="cpu")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def multi_hop_search(query_text, num_hops=1, top_k=3):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    context_chunks = []
    
    with driver.session(database=NEO4J_DATABASE) as session:
        if num_hops == 0:
            cypher_query = """
            MATCH (c:Chunk)-[:PART_OF]->(d:Document)
            RETURN c.chunk_id as chunk_id, c.text as text, d.doc_id as doc_id, d.title as doc_title
            LIMIT $top_k
            """
        else:
            cypher_query = f"""
            MATCH (c:Chunk)-[:PART_OF]->(d:Document)
            OPTIONAL MATCH path = (d)-[r:CAN_CU|THAY_THE|HOP_NHAT*1..{num_hops}]-(d_related:Document)
            OPTIONAL MATCH (c_rel:Chunk)-[:PART_OF]->(d_related)
            RETURN c.chunk_id as chunk_id, c.text as text, d.doc_id as doc_id, d.title as doc_title,
                   collect(DISTINCT c_rel.text)[..2] as related_texts,
                   collect(DISTINCT d_related.title) as related_docs
            LIMIT $top_k
            """

        results = session.run(cypher_query, top_k=top_k)
        
        for rec in results:
            item = f"[Tài liệu gốc: {rec['doc_title']} ({rec['doc_id']})]\n{rec['text']}"
            if num_hops > 0 and rec.get('related_texts'):
                rel_docs_str = ", ".join([str(doc) for doc in rec['related_docs'] if doc])
                rel_texts_str = "\n".join([str(txt) for txt in rec['related_texts'] if txt])
                if rel_texts_str.strip():
                    item += f"\n\n--> [Ngữ cảnh Mở rộng Multi-hop ({num_hops}-hop) - Văn bản liên quan: {rel_docs_str}]:\n{rel_texts_str}"
            context_chunks.append(item)

    driver.close()
    return "\n\n-------------------\n\n".join(context_chunks)

def ask_gemini(question, context):
    if not gemini_client:
        return "[Thông báo]: Đã trích xuất xong ngữ cảnh Multi-hop từ Neo4j. (Chưa cấu hình GEMINI_API_KEY để gọi LLM)."

    system_prompt = (
        "Bạn là một chuyên gia tư vấn pháp luật Việt Nam thông minh và chính xác.\n"
        "Nhiệm vụ của bạn là trả lời câu hỏi của người dùng DỰA HOÀN TOÀN vào Ngữ cảnh được cung cấp.\n"
        "Nếu ngữ cảnh không đủ thông tin, hãy tuyên bố rõ: 'Ngữ cảnh không cung cấp đủ thông tin để trả lời câu hỏi này'.\n"
    )

    full_prompt = f"{system_prompt}\n\n=== NGỮ CẢNH TRUY VẤN ===\n{context}\n\n=== CÂU HỎI ===\n{question}"

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"[Lỗi Gemini API]: {e}"

TEST_QUESTIONS = [
    "Nghị định 46/2023/NĐ-CP thay thế cho nghị định nào, và nghị định bị thay thế đó có nội dung gì nổi bật về kinh doanh bảo hiểm?",
    "Văn bản hợp nhất số 52/VBHN-NHNN được hợp nhất từ văn bản nào, và quy định về hồ sơ, thủ tục cấp giấy phép lần đầu của ngân hàng thương mại gồm những tài liệu gì?",
    "Thông tư số 01/2025/TT-NHNN quy định về cấp giấy phép quỹ tín dụng nhân dân được sửa đổi, bổ sung bởi văn bản nào, và những nội dung sửa đổi bổ sung chính là gì?",
    "Thông tư số 41/2016/TT-NHNN về tỷ lệ an toàn vốn của ngân hàng căn cứ vào luật nào, và luật đó quy định chức năng nhiệm vụ của cơ quan nào?",
    "Hoạt động giao nhận, vận chuyển tiền mặt và tài sản quý của Ngân hàng Nhà nước được điều chỉnh bởi Thông tư nào, và Thông tư đó có được sửa đổi bổ sung bởi văn bản nào không?"
]

def run_experiment():
    output_file = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_11/qa_comparison.md")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO ĐÁNH GIÁ SO SÁNH THỬ NGHIỆM MULTI-HOP GRAPH RAG (BUỔI 11)\n\n")
        
        for idx, q in enumerate(TEST_QUESTIONS, 1):
            print(f"\n[Đang xử lý Câu hỏi {idx}/5]: {q}")
            f.write(f"--- \n## Câu hỏi {idx}: {q}\n\n")

            for hops in [0, 1, 2]:
                print(f"  --> Chạy thử nghiệm với Hops = {hops}...")
                context = multi_hop_search(q, num_hops=hops, top_k=2)
                answer = ask_gemini(q, context)
                
                f.write(f"### 📍 Kết quả với {hops} Bước nhảy (Hops = {hops}):\n")
                f.write(f"**Trả lời:**\n{answer}\n\n")
                f.write(f"<details><summary>Xem Ngữ cảnh Trích xuất từ Graph Neo4j</summary>\n\n```text\n{context}\n```\n</details>\n\n")

    print(f"\n✔ Đã hoàn thành thử nghiệm! Kết quả so sánh đã xuất ra file: {output_file}")

if __name__ == "__main__":
    run_experiment()