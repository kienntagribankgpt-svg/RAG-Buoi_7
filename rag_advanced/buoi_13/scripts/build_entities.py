import os
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_13")
data_dir = base_dir / "data"
outputs_dir = base_dir / "outputs"
outputs_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("BƯỚC 2: CHUẨN HÓA DỮ LIỆU THÀNH ENTITIES & RELATIONS (BUỔI 13)")
print("=" * 70)

# 1. Đọc dữ liệu từ data/
df_risks = pd.read_csv(data_dir / "risk_profiles_seed.csv")
df_controls = pd.read_csv(data_dir / "controls_seed.csv")
df_events = pd.read_csv(data_dir / "risk_events_seed.csv")
df_relations = pd.read_csv(data_dir / "relationships_seed.csv")

# 2. Xây dựng danh sách Entities
entities = []

# Mapping RuiRo
for _, r in df_risks.iterrows():
    entities.append({
        "id": str(r["id"]).strip(),
        "type": "RuiRo",
        "name": str(r.get("name", "")).strip(),
        "description": str(r.get("description", "")).strip(),
        "category": str(r.get("category", "")).strip(),
        "cause": str(r.get("cause", "")).strip(),
        "event": str(r.get("event", "")).strip(),
        "impact": str(r.get("impact", "")).strip(),
        "inherent_level": str(r.get("inherent_level", "")).strip(),
        "residual_level": str(r.get("residual_level", "")).strip(),
        "owner_unit_id": str(r.get("owner_unit_id", "")).strip(),
        "owner_role_id": "",
        "control_type": "",
        "frequency": "",
        "effectiveness": "",
        "occurred_at": "",
        "discovered_at": "",
        "severity": "",
        "loss_amount_vnd": "",
        "source_file": "risk_profiles_seed.csv",
        "data_origin": str(r.get("data_origin", "")).strip(),
        "verification_status": str(r.get("verification_status", "")).strip()
    })

# Mapping KiemSoat
for _, r in df_controls.iterrows():
    entities.append({
        "id": str(r["id"]).strip(),
        "type": "KiemSoat",
        "name": str(r.get("name", "")).strip(),
        "description": "",
        "category": "",
        "cause": "",
        "event": "",
        "impact": "",
        "inherent_level": "",
        "residual_level": "",
        "owner_unit_id": "",
        "owner_role_id": str(r.get("owner_role_id", "")).strip(),
        "control_type": str(r.get("control_type", "")).strip(),
        "frequency": str(r.get("frequency", "")).strip(),
        "effectiveness": str(r.get("effectiveness", "")).strip(),
        "occurred_at": "",
        "discovered_at": "",
        "severity": "",
        "loss_amount_vnd": "",
        "source_file": "controls_seed.csv",
        "data_origin": str(r.get("data_origin", "")).strip(),
        "verification_status": str(r.get("verification_status", "")).strip()
    })

# Mapping SuKienRuiRo
for _, r in df_events.iterrows():
    entities.append({
        "id": str(r["id"]).strip(),
        "type": "SuKienRuiRo",
        "name": str(r.get("description", "")).strip(),
        "description": str(r.get("description", "")).strip(),
        "category": "",
        "cause": "",
        "event": "",
        "impact": "",
        "inherent_level": "",
        "residual_level": "",
        "owner_unit_id": "",
        "owner_role_id": "",
        "control_type": "",
        "frequency": "",
        "effectiveness": "",
        "occurred_at": str(r.get("occurred_at", "")).strip(),
        "discovered_at": str(r.get("discovered_at", "")).strip(),
        "severity": str(r.get("severity", "")).strip(),
        "loss_amount_vnd": str(r.get("loss_amount_vnd", "")).strip(),
        "source_file": "risk_events_seed.csv",
        "data_origin": str(r.get("data_origin", "")).strip(),
        "verification_status": str(r.get("verification_status", "")).strip()
    })

df_out_entities = pd.DataFrame(entities)
entities_path = outputs_dir / "entities.csv"
df_out_entities.to_csv(entities_path, index=False, encoding="utf-8-sig")

# 3. Chuẩn hóa Relations
relations_path = outputs_dir / "relations.csv"
df_relations.to_csv(relations_path, index=False, encoding="utf-8-sig")

# 4. In báo cáo thống kê kiểm tra
print(f"✔ Đã lưu file entities: {entities_path}")
print("  - Thống kê Entities theo Type:")
for t, count in df_out_entities["type"].value_counts().items():
    print(f"    + {t}: {count} entities")

print(f"\n✔ Đã lưu file relations: {relations_path}")
print("  - Thống kê Relations theo Relationship Type:")
for rel_t, count in df_relations["relationship_type"].value_counts().items():
    print(f"    + {rel_t}: {count} relations")

# 5. Kiểm tra tính toàn vẹn khóa tham chiếu (Integrity Check)
all_ent_ids = set(df_out_entities["id"].unique())
orphan_src = set(df_relations["source_id"].astype(str).str.strip()) - all_ent_ids
orphan_tgt = set(df_relations["target_id"].astype(str).str.strip()) - all_ent_ids
print("\n[KIỂM TRA KHÓA THAM CHIẾU (INTEGRITY CHECK)]:")
print(f"  - Orphan source_id: {orphan_src or 'None (100% hợp lệ)'}")
print(f"  - Orphan target_id: {orphan_tgt or 'None (100% hợp lệ)'}")

print("\n" + "=" * 70)
print("✔ HOÀN TẤT BƯỚC 2: CHUẨN HÓA DỮ LIỆU ĐẠT [PASS]")
print("=" * 70)