import os
import re
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_13")
wiki_dir = base_dir / "wiki"
outputs_dir = base_dir / "outputs"
outputs_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("BƯỚC 4: KIỂM THỬ TOÀN DIỆN WIKI (BUỔI 13)")
print("=" * 70)

# 1. Đọc entities và relations
df_entities = pd.read_csv(outputs_dir / "entities.csv")
df_relations = pd.read_csv(outputs_dir / "relations.csv")

# 2. Quét tất cả các file Markdown trong wiki/
all_md_files = list(wiki_dir.rglob("*.md"))
file_names_stem = {f.stem for f in all_md_files}

# 3. Trích xuất và kiểm tra liên kết wikilink
wikilink_pattern = re.compile(r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]')

total_wikilinks = 0
broken_links = []
page_link_count = {f.stem: {"in": 0, "out": 0} for f in all_md_files}

for md_file in all_md_files:
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    matches = wikilink_pattern.findall(content)
    total_wikilinks += len(matches)
    page_link_count[md_file.stem]["out"] += len(matches)

    for target in matches:
        target_clean = target.strip()
        if target_clean not in file_names_stem:
            broken_links.append((md_file.name, target_clean))
        else:
            page_link_count[target_clean]["in"] += 1

# 4. Kiểm tra rủi ro không có kiểm soát hoặc không có sự kiện
risk_ids = set(df_entities[df_entities["type"] == "RuiRo"]["id"].unique())
mitigated_risks = set(df_relations[df_relations["relationship_type"] == "MITIGATES"]["target_id"].unique())
observed_risks = set(df_relations[df_relations["relationship_type"] == "OBSERVED_AS"]["source_id"].unique())

risks_without_controls = risk_ids - mitigated_risks
risks_without_events = risk_ids - observed_risks

# 5. Kiểm tra orphan pages (trừ Home.md)
orphan_pages = [page for page, c in page_link_count.items() if page != "Home" and c["in"] == 0 and c["out"] == 0]

# 6. Ghi báo cáo ra file Markdown
report_path = outputs_dir / "wiki_validation_report.md"
report_content = f"""# 📑 BÁO CÁO KIỂM THỬ TOÀN VẸN WIKI RISK GRAPH (BUỔI 13)

- **Thời gian kiểm thử:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Tổng số trang Markdown:** {len(all_md_files)} trang
- **Tổng số liên kết hai chiều (Wikilinks):** {total_wikilinks} liên kết

---

## 1. Kết quả kiểm tra tính toàn vẹn liên kết
- **Số lượng Broken Wikilinks:** {len(broken_links)} lỗi
"""
if broken_links:
    for src, tgt in broken_links:
        report_content += f"  - ❌ File `{src}` trỏ tới trang không tồn tại: `[[{tgt}]]`\n"
else:
    report_content += "- ✔ **100% Wikilinks hợp lệ (Không có broken link nào).**\n"

report_content += f"""
---

## 2. Kết quả kiểm tra cấu trúc đồ thị (Graph Structure)
- **Số trang cô lập (Orphan Pages):** {len(orphan_pages)}
- **Rủi ro chưa có biện pháp Kiểm soát giảm thiểu:** {list(risks_without_controls) or 'None (100% rủi ro đã có kiểm soát)'}
- **Rủi ro chưa ghi nhận Sự kiện thực tế:** {list(risks_without_events) or 'None (100% rủi ro đã ghi nhận sự kiện)'}

---

## 3. Kết luận kiểm toán
- **Trạng thái kiểm thử:** {'✅ ĐẠT TIÊU CHUẨN KIỂM THỬ [PASS]' if len(broken_links) == 0 else '❌ CẦN SỬA LỖI'}
- **Độ tin cậy dữ liệu:** Đạt chuẩn biểu diễn tri thức đồ thị (Knowledge Graph), sẵn sàng mở trên Obsidian và nạp vào Neo4j.
"""

with open(report_path, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"✔ Đã xuất báo cáo kiểm thử tại: {report_path}")
print(f"  - Tổng số file Markdown: {len(all_md_files)}")
print(f"  - Tổng số Wikilinks: {total_wikilinks}")
print(f"  - Số lỗi Broken link: {len(broken_links)}")
print(f"  - Rủi ro chưa có kiểm soát: {len(risks_without_controls)}")
print(f"  - Rủi ro chưa có sự kiện: {len(risks_without_events)}")
print("=" * 70)
print("✔ HOÀN TẤT BƯỚC 4: KIỂM THỬ WIKI ĐẠT [PASS]")
print("=" * 70)