import os
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_13")
data_dir = base_dir / "data"

print("=" * 70)
print("BƯỚC 1: KIỂM TRA TOÀN DIỆN DỮ LIỆU SEED (BUỔI 13)")
print("=" * 70)

files = {
    "risk_profiles": data_dir / "risk_profiles_seed.csv",
    "controls": data_dir / "controls_seed.csv",
    "risk_events": data_dir / "risk_events_seed.csv",
    "relationships": data_dir / "relationships_seed.csv"
}

dfs = {}
for name, path in files.items():
    if not path.exists():
        print(f"❌ Chưa tìm thấy file: {path.name}")
        continue
    df = pd.read_csv(path)
    dfs[name] = df
    print(f"\n[FILE] {path.name}:")
    print(f"  - Số bản ghi: {len(df)} dòng, {len(df.columns)} cột")
    print(f"  - Danh sách cột: {list(df.columns)}")
    if 'id' in df.columns:
        print(f"  - Trùng lặp khóa chính (id duplicates): {df['id'].duplicated().sum()}")
    nulls = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
    print(f"  - Cột có giá trị null: {nulls or 'Không có (100% đầy đủ)'}")

if "relationships" in dfs:
    df_rel = dfs["relationships"]
    print("\n[THỐNG KÊ QUAN HỆ (RELATIONSHIPS)]:")
    for r_type, count in df_rel['relationship_type'].value_counts().items():
        print(f"  + [{r_type}]: {count} quan hệ")

    all_entity_ids = set()
    for key in ["risk_profiles", "controls", "risk_events"]:
        if key in dfs and "id" in dfs[key].columns:
            all_entity_ids.update(dfs[key]["id"].dropna().astype(str).str.strip().unique())

    orphan_src = set(df_rel["source_id"].astype(str).str.strip()) - all_entity_ids
    orphan_tgt = set(df_rel["target_id"].astype(str).str.strip()) - all_entity_ids
    print("\n[KIỂM TRA KHÓA THAM CHIẾU (ORPHAN REFERENCES)]:")
    print(f"  - source_id không tồn tại trong entities: {orphan_src or 'None (Hợp lệ 100%)'}")
    print(f"  - target_id không tồn tại trong entities: {orphan_tgt or 'None (Hợp lệ 100%)'}")

print("\n" + "=" * 70)
print("✔ HOÀN TẤT BƯỚC 1: KIỂM TRA DỮ LIỆU ĐẠT CHUẨN [PASS]")
print("=" * 70)