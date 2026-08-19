import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_14")
kb_hops_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_10/graph_rag_labs/kb+hops")

load_dotenv("D:/du_an_cua_ban/RAG/.env")
load_dotenv(base_dir / ".env")

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")

print("=" * 70)
print("PROMPT 6: NẠP KNOWLEDGE GRAPH MINI VÀO NEO4J (LAB_SESSION = 'buoi_14')")
print("=" * 70)

try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    driver.verify_connectivity()
    print("✔ Kết nối Neo4j thành công!")
except Exception as e:
    print(f"⚠ Neo4j chưa kết nối ({e}). Bỏ qua nạp database và ghi nhận trạng thái.")
    (base_dir / "outputs" / "kg_build_report.md").write_text(f"# KG Build Report\n- Status: NOT RUN ({e})", encoding="utf-8")
    sys.exit(0)

df_corpus = pd.read_csv(base_dir / "data" / "processed" / "chunks_normalized.csv")
df_meta = pd.read_csv(kb_hops_dir / "metadata.csv")
df_rel = pd.read_csv(kb_hops_dir / "relationships.csv")

with driver.session() as session:
    # 1. Dọn dẹp an toàn chỉ dữ liệu của buoi_14
    session.run("MATCH (n {lab_session: 'buoi_14'}) DETACH DELETE n")
    
    # 2. Nạp Node Văn Bản
    for _, r in df_meta.iterrows():
        session.run("""
            MERGE (v:VanBan {id: $id})
            SET v.title = $title,
                v.so_ky_hieu = $so_ky_hieu,
                v.loai_vb = $loai_vb,
                v.lab_session = 'buoi_14'
        """, id=str(r["id"]), title=str(r.get("title", "")), so_ky_hieu=str(r.get("so_ky_hieu", "")), loai_vb=str(r.get("loai_van_ban", "")))
        
    # 3. Nạp Node Điều Khoản & quan hệ CONTAINS, NEXT
    prev_chunk_id = None
    prev_doc_id = None
    for _, r in df_corpus.iterrows():
        c_id = str(r["chunk_id"])
        d_id = str(r["document_id"])
        session.run("""
            MERGE (d:DieuKhoan {id: $id})
            SET d.text = $text,
                d.article = $article,
                d.document_id = $doc_id,
                d.lab_session = 'buoi_14'
            WITH d
            MATCH (v:VanBan {id: $doc_id})
            MERGE (v)-[:CONTAINS {lab_session: 'buoi_14'}]->(d)
        """, id=c_id, text=str(r["text"])[:300], article=str(r["article"]), doc_id=d_id)
        
        # Quan hệ cấu trúc NEXT giữa các điều khoản cùng một văn bản
        if prev_doc_id == d_id and prev_chunk_id:
            session.run("""
                MATCH (d1:DieuKhoan {id: $id1}), (d2:DieuKhoan {id: $id2})
                MERGE (d1)-[:NEXT {lab_session: 'buoi_14'}]->(d2)
            """, id1=prev_chunk_id, id2=c_id)
        prev_chunk_id = c_id
        prev_doc_id = d_id
        
    # 4. Nạp các quan hệ pháp lý thực tế từ relationships.csv
    for _, r in df_rel.iterrows():
        rel_type = str(r.get("relationship_type", r.get("relationship", "THAM_CHIEU"))).upper().replace(" ", "_")
        session.run(f"""
            MATCH (v1:VanBan {{id: $doc1}}), (v2:VanBan {{id: $doc2}})
            MERGE (v1)-[:{rel_type} {{lab_session: 'buoi_14'}}]->(v2)
        """, doc1=str(r["doc_id"]), doc2=str(r["other_doc_id"]))

    res_vb = session.run("MATCH (n:VanBan {lab_session: 'buoi_14'}) RETURN count(n) as count").single()["count"]
    res_dk = session.run("MATCH (n:DieuKhoan {lab_session: 'buoi_14'}) RETURN count(n) as count").single()["count"]
    res_rel = session.run("MATCH ()-[r {lab_session: 'buoi_14'}]->() RETURN count(r) as count").single()["count"]

print(f"✔ Đã nạp thành công vào Neo4j:")
print(f"   - {res_vb} Node Văn Bản (:VanBan)")
print(f"   - {res_dk} Node Điều Khoản (:DieuKhoan)")
print(f"   - {res_rel} Mối quan hệ liên kết (:CONTAINS, :NEXT, :RELATIONS)")

report_lines = [
    "# 🌐 BÁO CÁO XÂY DỰNG KNOWLEDGE GRAPH MINI (BUỔI 14)\n",
    f"- **Tổng số Node VanBan**: {res_vb}",
    f"- **Tổng số Node DieuKhoan**: {res_dk}",
    f"- **Tổng số Quan hệ (Relationships)**: {res_rel}",
    f"- **Trạng thái**: THÀNH CÔNG (SUCCESS)"
]
(base_dir / "outputs" / "kg_build_report.md").write_text("\n".join(report_lines), encoding="utf-8")
driver.close()