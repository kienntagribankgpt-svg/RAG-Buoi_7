import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

def test_neo4j_output():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    with driver.session(database=NEO4J_DATABASE) as session:
        print("\n" + "="*65)
        print("=== BÁO CÁO KIỂM TRA ĐẦU RA OUTPUT TRONG NEO4J ===")
        print("="*65)
        
        # 1. Kiểm tra Nút Document
        doc_res = session.run("MATCH (d:Document) RETURN count(d) as total").single()
        print(f" Tổng số Nút Document: {doc_res['total']}")
        
        # 2. Kiểm tra Quan hệ giữa các Document
        rel_res = session.run("MATCH (:Document)-[r:CAN_CU|THAY_THE|HOP_NHAT]->(:Document) RETURN count(r) as total").single()
        print(f" Tổng số Quan hệ Document: {rel_res['total']}")
        
        # 3. Kiểm tra Nút Chunk & Vector Dim
        chunk_res = session.run("MATCH (c:Chunk) RETURN count(c) as total").single()
        print(f" Tổng số Nút Chunk: {chunk_res['total']}")
        
        print("-" * 65)
        print("DỮ LIỆU MẪU CÁC NÚT CHUNK ĐÃ NẠP:")
        sample_chunks = session.run("MATCH (c:Chunk) RETURN c.chunk_id as id, c.chapter as chap, c.article as art, size(c.embedding) as emb_dim LIMIT 3")
        for rec in sample_chunks:
            print(f" • [Chunk ID]: {rec['id']} | Phân cấp: {rec['chap']} -> {rec['art']} | Vector Dim: {rec['emb_dim']}")
            
        print("="*65 + "\n")
        
    driver.close()

if __name__ == "__main__":
    try:
        test_neo4j_output()
    except Exception as e:
        print(f"\n[Lỗi kết nối]: {e}")