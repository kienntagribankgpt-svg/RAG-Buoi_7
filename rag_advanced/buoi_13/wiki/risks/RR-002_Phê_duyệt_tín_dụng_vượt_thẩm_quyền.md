---
id: RR-002
type: RuiRo
name: "Phê duyệt tín dụng vượt thẩm quyền"
category: "Rui ro tin dung"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-CREDIT"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-002 - Phê duyệt tín dụng vượt thẩm quyền

## 1. Mô tả & Diễn biến
- **Mô tả:** Kiểm tra hạn mức phê duyệt không hiệu lực
- **Nguyên nhân (Cause):** Phân quyền trên hệ thống không cập nhật
- **Sự kiện kích hoạt (Event):** Khoản vay được phê duyệt vượt thẩm quyền
- **Hậu quả & Tác động (Impact):** Tăng nợ xấu và vi phạm quy định

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-002_Kiểm_tra_hạn_mức_phê_duyệt_trên_hệ_thống|KS-002 - Kiểm tra hạn mức phê duyệt trên hệ thống]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: kiểm tra hạn mức ngăn phê duyệt vượt thẩm quyền"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-002_Hồ_sơ_tín_dụng_được_phê_duyệt_vượt_hạn_m|SK-002 - Hồ sơ tín dụng được phê duyệt vượt hạn mức của người phê duyệt]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện vượt thẩm quyền"
