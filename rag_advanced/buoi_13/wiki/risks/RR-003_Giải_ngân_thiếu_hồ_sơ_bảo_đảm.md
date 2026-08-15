---
id: RR-003
type: RuiRo
name: "Giải ngân thiếu hồ sơ bảo đảm"
category: "Rui ro tin dung"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-CREDIT"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-003 - Giải ngân thiếu hồ sơ bảo đảm

## 1. Mô tả & Diễn biến
- **Mô tả:** Hồ sơ giải ngân chưa đủ điều kiện
- **Nguyên nhân (Cause):** Kiểm tra điều kiện tiên quyết bị bỏ qua
- **Sự kiện kích hoạt (Event):** Giải ngân khi thiếu chứng từ bắt buộc
- **Hậu quả & Tác động (Impact):** Khó thu hồi nợ và vi phạm quy trình

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-003_Checklist_điều_kiện_giải_ngân_bắt_buộc|KS-003 - Checklist điều kiện giải ngân bắt buộc]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: checklist ngăn giải ngân thiếu hồ sơ"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-003_Giải_ngân_trước_khi_hoàn_thiện_chứng_từ_|SK-003 - Giải ngân trước khi hoàn thiện chứng từ bảo đảm]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện giải ngân thiếu hồ sơ"
