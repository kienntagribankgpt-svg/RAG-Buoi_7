import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_15")
load_dotenv("D:/du_an_cua_ban/RAG/.env")
load_dotenv(base_dir / ".env")

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")

try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    driver.verify_connectivity()
    print("✔ Kết nối Neo4j thành công!")
except Exception as e:
    print(f"⚠ Neo4j chưa kết nối ({e}). Bỏ qua cập nhật Neo4j.")
    driver = None

if driver:
    df_secure = pd.read_csv(base_dir / "data" / "processed" / "chunks_secure.csv")
    
    with driver.session() as session:
        print("[*] Đang cập nhật thuộc tính allowed_roles vào đồ thị Neo4j...")
        for _, row in df_secure.iterrows():
            c_id = str(row["chunk_id"])
            roles = row["allowed_roles"]
            if isinstance(roles, str):
                roles = json.loads(roles.replace("'", '"'))
            
            session.run("""
                MATCH (d:DieuKhoan {id: $id})
                SET d.allowed_roles = $roles,
                    d.lab_session = 'buoi_15'
            """, id=c_id, roles=roles)
            
            session.run("""
                MATCH (v:VanBan {id: $doc_id})
                SET v.allowed_roles = $roles,
                    v.lab_session = 'buoi_15'
            """, doc_id=str(row["document_id"]), roles=roles)
            
        cnt_d = session.run("MATCH (d:DieuKhoan) WHERE d.allowed_roles IS NOT NULL RETURN count(d) as c").single()["c"]
        cnt_v = session.run("MATCH (v:VanBan) WHERE v.allowed_roles IS NOT NULL RETURN count(v) as c").single()["c"]
        print(f"✔ Đã cập nhật bảo mật cho {cnt_v} Node Văn Bản và {cnt_d} Node Điều Khoản trên Neo4j!")
    driver.close()
