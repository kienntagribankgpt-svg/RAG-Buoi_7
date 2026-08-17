import json
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_15")
input_file = base_dir / "data" / "processed" / "chunks_normalized.csv"
output_file = base_dir / "data" / "processed" / "chunks_secure.csv"

df = pd.read_csv(input_file)

def classify_roles(row):
    text_lower = str(row.get("text", "")).lower()
    doc_id = str(row.get("document_id", ""))
    
    # 1. Nhóm tài liệu Nhân sự / Lương thưởng / Bổ nhiệm
    if any(k in text_lower for k in ["nhân sự", "lương", "tuyển dụng", "bổ nhiệm", "kỷ luật", "thù lao", "hội đồng đầu tư"]):
        return ["Admin", "HR"]
        
    # 2. Nhóm tài liệu Quản trị rủi ro / Hạn mức / Cấp tín dụng / Cho vay
    elif any(k in text_lower for k in ["tín dụng", "cho vay", "rủi ro", "hạn mức", "phê duyệt", "bảo lãnh", "quỹ bảo đảm"]):
        return ["Admin", "Risk_Manager", "Staff"]
        
    # 3. Nhóm tài liệu Quy định chung / Công khai
    else:
        return ["Admin", "HR", "Risk_Manager", "Staff", "Guest"]

df["allowed_roles"] = df.apply(classify_roles, axis=1)

# Lưu dưới dạng json string để dễ phân tích trong Pandas & CSV
df["allowed_roles_str"] = df["allowed_roles"].apply(json.dumps)

df.to_csv(output_file, index=False, encoding="utf-8")

print("=" * 70)
print("✔ GÁN THẺ BẢO MẬT (SECURITY TAGGING) THÀNH CÔNG!")
print("=" * 70)
print(f"Tổng số chunks đã gán quyền: {len(df)}")
role_dist = df["allowed_roles"].apply(lambda x: "+".join(x)).value_counts()
print("\nPhân bố các cấp độ bảo mật:")
for k, v in role_dist.items():
    print(f" - [{k}]: {v} chunks")
print(f"\n✔ File lưu tại: {output_file}")
