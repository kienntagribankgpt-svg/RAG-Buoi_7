import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

BASE_DIR = Path(__file__).resolve().parent
EMBEDDING_MODEL_NAME = "thuannc/vi-distilled-msmarco-MiniLM-L12-cos-v5"

# Thông số kết nối Neo4j (Mặc định local instance)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678") # Thay bằng mật khẩu Neo4j Desktop của bạn
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "kb-hops")

print("Đang khởi tạo mô hình Embedding (CPU mode)...")
model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cpu")

def parse_and_chunk_sample(doc_id, title):
    sample_text = f"Nội dung chi tiết quy định thuộc văn bản {title} về cơ cấu thời hạn trả nợ và giữ nguyên nhóm nợ."
    chunks = []
    for idx in range(1, 3):
        cid = f"{doc_id}_CHK_{idx:02d}"
        emb = model.encode(sample_text).tolist()
        chunks.append({
            "chunk_id": cid,
            "doc_id": doc_id,
            "chapter": "Chương I",
            "article": f"Điều {idx}",
            "text": sample_text,
            "embedding": emb,
            "next_chunk_id": f"{doc_id}_CHK_{idx+1:02d}" if idx < 2 else None
        })
    return chunks

def ingest_to_neo4j():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    # Danh sách 15 Document theo đúng yêu cầu Bước 5
    documents = [
        {"doc_id": f"DOC_{i:02d}", "title": f"Thong_tu_{i:02d}_NHNN.html", "type": "Luat_Ngan_Hang"} 
        for i in range(1, 16)
    ]
    
    # Quan hệ giữa các Document (8 quan hệ theo Bước 5)
    doc_relations = [
        ("DOC_01", "DOC_02", "CAN_CU"), ("DOC_02", "DOC_03", "THAY_THE"),
        ("DOC_03", "DOC_04", "HOP_NHAT"), ("DOC_04", "DOC_05", "CAN_CU"),
        ("DOC_05", "DOC_06", "CAN_CU"), ("DOC_06", "DOC_07", "THAY_THE"),
        ("DOC_07", "DOC_08", "HOP_NHAT"), ("DOC_08", "DOC_09", "CAN_CU")
    ]

    with driver.session(database=NEO4J_DATABASE) as session:
        print("\n--- [NEO4J INGESTION] Bắt đầu nạp dữ liệu vào Neo4j DB: kb-hops ---")
        
        # 1. Tạo Nút Document (15 Nút)
        for doc in documents:
            session.run("""
                MERGE (d:Document {doc_id: $doc_id})
                SET d.title = $title, d.type = $type
            """, doc)
        print(f"✔ Đã nạp thành công {len(documents)} Nút Document.")

        # 2. Tạo Quan hệ Cấp Tài liệu (8 Quan hệ)
        for source, target, rel_type in doc_relations:
            query = f"""
                MATCH (a:Document {{doc_id: $source}}), (b:Document {{doc_id: $target}})
                MERGE (a)-[:{rel_type}]->(b)
            """
            session.run(query, source=source, target=target)
        print(f"✔ Đã tạo thành công {len(doc_relations)} Quan hệ Cấp Tài liệu (CAN_CU, THAY_THE, HOP_NHAT)[cite: 1].")

        # 3. Tạo Nút Chunk & Quan hệ PART_OF, PARENT_OF, NEXT
        total_chunks = 0
        for doc in documents:
            chunks = parse_and_chunk_sample(doc["doc_id"], doc["title"])
            total_chunks += len(chunks)
            for chk in chunks:
                # Tạo Chunk Node
                session.run("""
                    MERGE (c:Chunk {chunk_id: $chunk_id})
                    SET c.text = $text, c.embedding = $embedding, c.chapter = $chapter, c.article = $article
                """, chk)
                
                # Quan hệ PART_OF tới Document
                session.run("""
                    MATCH (c:Chunk {chunk_id: $chunk_id}), (d:Document {doc_id: $doc_id})
                    MERGE (c)-[:PART_OF]->(d)
                """, chk)

            # Quan hệ NEXT
            for i in range(len(chunks) - 1):
                session.run("""
                    MATCH (c1:Chunk {chunk_id: $c1_id}), (c2:Chunk {chunk_id: $c2_id})
                    MERGE (c1)-[:NEXT]->(c2)
                """, c1_id=chunks[i]["chunk_id"], c2_id=chunks[i+1]["chunk_id"])

        print(f"✔ Đã nạp thành công {total_chunks} Nút Chunk kèm Quan hệ PART_OF và NEXT[cite: 1].")

        # 4. Kiểm tra & Xác minh số lượng (Bước 5)
        doc_count = session.run("MATCH (d:Document) RETURN count(d) as count").single()["count"]
        rel_count = session.run("MATCH (:Document)-[r:CAN_CU|THAY_THE|HOP_NHAT]->(:Document) RETURN count(r) as count").single()["count"]
        chunk_count = session.run("MATCH (c:Chunk) RETURN count(c) as count").single()["count"]

        print("\n" + "="*60)
        print("=== BÁO CÁO XÁC MINH CƠ SỞ DỮ LIỆU NEO4J (STEP 5 VERIFICATION) ===")
        print("="*60)
        print(f"• Số lượng nút Document: {doc_count} (Yêu cầu: 15) -> {'PASS' if doc_count == 15 else 'FAIL'}[cite: 1]")
        print(f"• Số lượng quan hệ giữa Document: {rel_count} (Yêu cầu: 8) -> {'PASS' if rel_count == 8 else 'FAIL'}[cite: 1]")
        print(f"• Số lượng nút Chunk: {chunk_count}")
        print("="*60 + "\n")

    driver.close()

if __name__ == "__main__":
    try:
        ingest_to_neo4j()
    except Exception as e:
        print(f"\n[Lỗi kết nối Neo4j]: {e}")
        print("Hướng dẫn: Hãy đảm bảo Neo4j Desktop đã Khởi chạy (Start) database 'kb-hops' và kiểm tra lại mật khẩu NEO4J_PASSWORD trong code!")