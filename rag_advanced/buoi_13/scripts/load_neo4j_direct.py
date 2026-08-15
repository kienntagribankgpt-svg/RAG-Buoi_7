import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_13")
load_dotenv("D:/du_an_cua_ban/.env")

outputs_dir = base_dir / "outputs"

neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "12345678") # Tự động lấy pass hoặc mặc định

print("=" * 70)
print("ĐANG NẠP DỮ LIỆU WIKI RISK GRAPH VÀO NEO4J...")
print(f"URI: {neo4j_uri} | User: {neo4j_user}")
print("=" * 70)

from neo4j import GraphDatabase

try:
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    driver.verify_connectivity()
    print("✔ Kết nối Neo4j thành công!")
    
    df_entities = pd.read_csv(outputs_dir / "entities.csv")
    df_relations = pd.read_csv(outputs_dir / "relations.csv")
    
    with driver.session() as session:
        # Nạp RuiRo
        for _, r in df_entities[df_entities["type"] == "RuiRo"].iterrows():
            session.run("""
                MERGE (n:RuiRo {id: $id})
                SET n.name = $name, n.description = $description, n.category = $category,
                    n.inherent_level = $inherent_level, n.residual_level = $residual_level,
                    n.owner_unit_id = $owner_unit_id, n.verification_status = $verification_status
            """, dict(r))
            
        # Nạp KiemSoat
        for _, c in df_entities[df_entities["type"] == "KiemSoat"].iterrows():
            session.run("""
                MERGE (n:KiemSoat {id: $id})
                SET n.name = $name, n.control_type = $control_type, n.frequency = $frequency,
                    n.effectiveness = $effectiveness, n.owner_role_id = $owner_role_id,
                    n.verification_status = $verification_status
            """, dict(c))
            
        # Nạp SuKienRuiRo
        for _, e in df_entities[df_entities["type"] == "SuKienRuiRo"].iterrows():
            session.run("""
                MERGE (n:SuKienRuiRo {id: $id})
                SET n.name = $name, n.description = $description, n.occurred_at = $occurred_at,
                    n.discovered_at = $discovered_at, n.severity = $severity,
                    n.loss_amount_vnd = $loss_amount_vnd, n.verification_status = $verification_status
            """, dict(e))
            
        # Nạp Relations
        for _, rel in df_relations.iterrows():
            src_id = str(rel["source_id"]).strip()
            tgt_id = str(rel["target_id"]).strip()
            r_type = str(rel["relationship_type"]).strip()
            quote = str(rel.get("evidence_quote", ""))
            status = str(rel.get("verification_status", ""))
            
            if r_type == "MITIGATES":
                session.run("""
                    MATCH (k:KiemSoat {id: $src}), (r:RuiRo {id: $tgt})
                    MERGE (k)-[rel:MITIGATES]->(r)
                    SET rel.evidence_quote = $quote, rel.verification_status = $status
                """, src=src_id, tgt=tgt_id, quote=quote, status=status)
            elif r_type == "OBSERVED_AS":
                session.run("""
                    MATCH (r:RuiRo {id: $src}), (e:SuKienRuiRo {id: $tgt})
                    MERGE (r)-[rel:OBSERVED_AS]->(e)
                    SET rel.evidence_quote = $quote, rel.verification_status = $status
                """, src=src_id, tgt=tgt_id, quote=quote, status=status)
                
    print("✔ ĐÃ NẠP XONG TOÀN BỘ DỮ LIỆU BUỔI 13 VÀO NEO4J!")
    driver.close()
except Exception as ex:
    print(f"❌ Lỗi: {ex}")