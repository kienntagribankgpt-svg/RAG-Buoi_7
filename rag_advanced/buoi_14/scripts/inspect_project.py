import os
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_14")
kb_hops_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_10/graph_rag_labs/kb+hops")
outputs_dir = base_dir / "outputs"

print("=" * 70)
print("PROMPT 0: KIỂM TRA MÔI TRƯỜNG VÀ DỮ LIỆU NGUỒN BUỔI 14")
print("=" * 70)
print(f"[*] Thư mục dữ liệu nguồn: {kb_hops_dir}")

metadata_path = kb_hops_dir / "metadata.csv"
content_path = kb_hops_dir / "content.csv"
relations_path = kb_hops_dir / "relationships.csv"

report_lines = [
    "# BÁO CÁO KIỂM TRA TIỀN TRẠM (PROMPT 0 - BUỔI 14)\n",
    f"- **Working root**: `{base_dir}`",
    f"- **Nguồn dữ liệu**: `{kb_hops_dir}`\n"
]

all_files_ok = True
for name, p in [("metadata.csv", metadata_path), ("content.csv", content_path), ("relationships.csv", relations_path)]:
    if p.exists():
        df = pd.read_csv(p)
        print(f"✔ {name}: {len(df)} dòng, Cột: {list(df.columns)}")
        report_lines.append(f"### File `{name}`")
        report_lines.append(f"- **Số dòng**: {len(df)}")
        report_lines.append(f"- **Các cột**: `{list(df.columns)}`")
        report_lines.append(f"- **Số giá trị null**: {dict(df.isnull().sum())}\n")
    else:
        print(f"❌ Không tìm thấy: {p}")
        report_lines.append(f"### File `{name}`: ❌ KHÔNG TÌM THẤY")
        all_files_ok = False

report_content = "\n".join(report_lines)
(outputs_dir / "inspection_report.md").write_text(report_content, encoding="utf-8")

print("\n" + "=" * 70)
print("PROJECT PRE-CHECK:")
print(f"Working root: {base_dir}")
print(f"Data: {'ĐẦY ĐỦ 3 FILE' if all_files_ok else 'THIẾU FILE DỮ LIỆU'}")
print(f"Safe to continue: {'YES' if all_files_ok else 'NO'}")
print("=" * 70)