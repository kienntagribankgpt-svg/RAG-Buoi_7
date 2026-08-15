---
id: RR-008
type: RuiRo
name: "Định giá tài sản bảo đảm không chính xác"
category: "Rui ro tin dung"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-CREDIT"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-008 - Định giá tài sản bảo đảm không chính xác

## 1. Mô tả & Diễn biến
- **Mô tả:** Dữ liệu định giá không độc lập hoặc hết hạn
- **Nguyên nhân (Cause):** Thiếu rà soát lại giá trị tài sản
- **Sự kiện kích hoạt (Event):** Tài sản bảo đảm được định giá cao hơn thực tế
- **Hậu quả & Tác động (Impact):** Tăng tổn thất khi xử lý nợ

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-008_Rà_soát_độc_lập_định_giá_tài_sản_bảo_đảm|KS-008 - Rà soát độc lập định giá tài sản bảo đảm]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: rà soát độc lập giảm sai định giá"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-008_Rà_soát_phát_hiện_giá_trị_tài_sản_bảo_đả|SK-008 - Rà soát phát hiện giá trị tài sản bảo đảm đã hết hiệu lực]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện sai định giá tài sản"
