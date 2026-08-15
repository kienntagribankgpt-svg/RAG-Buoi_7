import os
import re
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_13")
outputs_dir = base_dir / "outputs"
wiki_dir = base_dir / "wiki"

risks_dir = wiki_dir / "risks"
controls_dir = wiki_dir / "controls"
events_dir = wiki_dir / "events"

for d in [risks_dir, controls_dir, events_dir]:
    d.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("BƯỚC 3: TỰ ĐỘNG SINH WIKI MARKDOWN (BUỔI 13)")
print("=" * 70)

df_entities = pd.read_csv(outputs_dir / "entities.csv")
df_relations = pd.read_csv(outputs_dir / "relations.csv")

entity_map = {str(r["id"]).strip(): r for _, r in df_entities.iterrows()}

def clean_filename(name):
    clean = re.sub(r'[\\/*?:"<>|]', '', str(name))
    return clean.strip().replace(" ", "_")

# 1. Tạo trang Risks (wiki/risks/)
risk_count = 0
for _, r in df_entities[df_entities["type"] == "RuiRo"].iterrows():
    r_id = str(r["id"]).strip()
    r_name = str(r.get("name", "")).strip()
    file_name = f"{r_id}_{clean_filename(r_name)[:40]}.md"
    file_path = risks_dir / file_name

    mitigating_controls = df_relations[(df_relations["target_id"] == r_id) & (df_relations["relationship_type"] == "MITIGATES")]
    observed_events = df_relations[(df_relations["source_id"] == r_id) & (df_relations["relationship_type"] == "OBSERVED_AS")]

    content = f"""---
id: {r_id}
type: RuiRo
name: "{r_name}"
category: "{r.get('category', '')}"
inherent_level: "{r.get('inherent_level', '')}"
residual_level: "{r.get('residual_level', '')}"
owner_unit_id: "{r.get('owner_unit_id', '')}"
verification_status: "{r.get('verification_status', '')}"
data_origin: "{r.get('data_origin', '')}"
---

# Rủi ro: {r_id} - {r_name}

## 1. Mô tả & Diễn biến
- **Mô tả:** {r.get('description', '')}
- **Nguyên nhân (Cause):** {r.get('cause', '')}
- **Sự kiện kích hoạt (Event):** {r.get('event', '')}
- **Hậu quả & Tác động (Impact):** {r.get('impact', '')}

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
"""
    if len(mitigating_controls) > 0:
        for _, rel in mitigating_controls.iterrows():
            c_id = str(rel["source_id"]).strip()
            c_info = entity_map.get(c_id, {})
            c_name = c_info.get("name", c_id)
            c_file = f"{c_id}_{clean_filename(c_name)[:40]}"
            content += f"- [[{c_file}|{c_id} - {c_name}]]\n"
            content += f"  - *Quan hệ:* `{rel['relationship_type']}` | *Trạng thái:* `{rel['verification_status']}`\n"
            content += f"  - *Bằng chứng trích dẫn:* \"{rel['evidence_quote']}\"\n"
    else:
        content += "- *Chưa có biện pháp kiểm soát nào được ghi nhận.*\n"

    content += "\n## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)\n"
    if len(observed_events) > 0:
        for _, rel in observed_events.iterrows():
            e_id = str(rel["target_id"]).strip()
            e_info = entity_map.get(e_id, {})
            e_desc = e_info.get("description", e_id)
            e_file = f"{e_id}_{clean_filename(e_desc)[:40]}"
            content += f"- [[{e_file}|{e_id} - {e_desc}]]\n"
            content += f"  - *Quan hệ:* `{rel['relationship_type']}` | *Trạng thái:* `{rel['verification_status']}`\n"
            content += f"  - *Bằng chứng trích dẫn:* \"{rel['evidence_quote']}\"\n"
    else:
        content += "- *Chưa ghi nhận sự kiện rủi ro thực tế.*\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    risk_count += 1

# 2. Tạo trang Controls (wiki/controls/)
control_count = 0
for _, c in df_entities[df_entities["type"] == "KiemSoat"].iterrows():
    c_id = str(c["id"]).strip()
    c_name = str(c.get("name", "")).strip()
    file_name = f"{c_id}_{clean_filename(c_name)[:40]}.md"
    file_path = controls_dir / file_name

    mitigated_risks = df_relations[(df_relations["source_id"] == c_id) & (df_relations["relationship_type"] == "MITIGATES")]

    content = f"""---
id: {c_id}
type: KiemSoat
name: "{c_name}"
control_type: "{c.get('control_type', '')}"
frequency: "{c.get('frequency', '')}"
effectiveness: "{c.get('effectiveness', '')}"
owner_role_id: "{c.get('owner_role_id', '')}"
verification_status: "{c.get('verification_status', '')}"
data_origin: "{c.get('data_origin', '')}"
---

# Kiểm soát: {c_id} - {c_name}

## 1. Thông tin kiểm soát
- **Loại kiểm soát:** {c.get('control_type', '')}
- **Tần suất:** {c.get('frequency', '')}
- **Hiệu quả đánh giá:** {c.get('effectiveness', '')}
- **Vai trò chịu trách nhiệm:** `{c.get('owner_role_id', '')}`

## 2. Rủi ro được giảm thiểu (MITIGATES)
"""
    if len(mitigated_risks) > 0:
        for _, rel in mitigated_risks.iterrows():
            r_id = str(rel["target_id"]).strip()
            r_info = entity_map.get(r_id, {})
            r_name = r_info.get("name", r_id)
            r_file = f"{r_id}_{clean_filename(r_name)[:40]}"
            content += f"- [[{r_file}|{r_id} - {r_name}]]\n"
            content += f"  - *Bằng chứng trích dẫn:* \"{rel['evidence_quote']}\"\n"
    else:
        content += "- *Chưa liên kết rủi ro cụ thể.*\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    control_count += 1

# 3. Tạo trang Events (wiki/events/)
event_count = 0
for _, e in df_entities[df_entities["type"] == "SuKienRuiRo"].iterrows():
    e_id = str(e["id"]).strip()
    e_desc = str(e.get("description", "")).strip()
    file_name = f"{e_id}_{clean_filename(e_desc)[:40]}.md"
    file_path = events_dir / file_name

    source_risks = df_relations[(df_relations["target_id"] == e_id) & (df_relations["relationship_type"] == "OBSERVED_AS")]

    content = f"""---
id: {e_id}
type: SuKienRuiRo
occurred_at: "{e.get('occurred_at', '')}"
discovered_at: "{e.get('discovered_at', '')}"
severity: "{e.get('severity', '')}"
loss_amount_vnd: "{e.get('loss_amount_vnd', '')}"
verification_status: "{e.get('verification_status', '')}"
data_origin: "{e.get('data_origin', '')}"
---

# Sự kiện rủi ro: {e_id}

## 1. Chi tiết sự kiện
- **Mô tả sự cố:** {e_desc}
- **Thời điểm phát sinh:** {e.get('occurred_at', '')}
- **Thời điểm phát hiện:** {e.get('discovered_at', '')}
- **Mức độ nghiêm trọng:** {e.get('severity', '')}
- **Tổn thất ước tính (VND):** {e.get('loss_amount_vnd', '')}

## 2. Nguồn gốc Rủi ro (OBSERVED_AS)
"""
    if len(source_risks) > 0:
        for _, rel in source_risks.iterrows():
            r_id = str(rel["source_id"]).strip()
            r_info = entity_map.get(r_id, {})
            r_name = r_info.get("name", r_id)
            r_file = f"{r_id}_{clean_filename(r_name)[:40]}"
            content += f"- [[{r_file}|{r_id} - {r_name}]]\n"
            content += f"  - *Bằng chứng trích dẫn:* \"{rel['evidence_quote']}\"\n"
    else:
        content += "- *Chưa xác định rủi ro gốc.*\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    event_count += 1

# 4. Tạo trang chủ Home.md
home_content = f"""---
title: "Wiki Tri Thức Quản Trị Rủi Ro"
type: "Overview"
---

# 🛡️ TRANG CHỦ WIKI TRI THỨC RỦI RO (RISK KNOWLEDGE GRAPH)

Chào mừng bạn đến với hệ sinh thái quản trị rủi ro dạng đồ thị.

## 📊 Thống kê Hệ thống
- **Tổng số Hồ sơ Rủi ro (RuiRo):** {risk_count} trang
- **Tổng số Biện pháp Kiểm soát (KiemSoat):** {control_count} trang
- **Tổng số Sự kiện Rủi ro (SuKienRuiRo):** {event_count} trang
- **Tổng số Mối quan hệ liên kết (Edges):** {len(df_relations)} quan hệ

---

## 🗂️ Danh mục hồ sơ tra cứu nhanh:
- 🔴 [Danh mục Hồ sơ Rủi ro (Risks)](./risks/)
- 🔵 [Danh mục Biện pháp Kiểm soát (Controls)](./controls/)
- 🟡 [Danh mục Sự kiện Rủi ro (Events)](./events/)
"""
with open(wiki_dir / "Home.md", "w", encoding="utf-8") as f:
    f.write(home_content)

print(f"✔ Đã tạo thành công {risk_count} trang Risks.")
print(f"✔ Đã tạo thành công {control_count} trang Controls.")
print(f"✔ Đã tạo thành công {event_count} trang Events.")
print(f"✔ Đã tạo trang chủ Home.md.")
print("=" * 70)
print("✔ HOÀN TẤT BƯỚC 3: SINH WIKI MARKDOWN ĐẠT [PASS]")
print("=" * 70)