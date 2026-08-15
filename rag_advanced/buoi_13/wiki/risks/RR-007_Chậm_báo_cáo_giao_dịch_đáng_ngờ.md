---
id: RR-007
type: RuiRo
name: "Chậm báo cáo giao dịch đáng ngờ"
category: "Rui ro tuan thu"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-COMPLIANCE"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-007 - Chậm báo cáo giao dịch đáng ngờ

## 1. Mô tả & Diễn biến
- **Mô tả:** Theo dõi cảnh báo AML không kịp thời
- **Nguyên nhân (Cause):** Khối lượng cảnh báo vượt năng lực xử lý
- **Sự kiện kích hoạt (Event):** Báo cáo giao dịch đáng ngờ nộp muộn
- **Hậu quả & Tác động (Impact):** Chế tài và rủi ro pháp lý

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-007_Theo_dõi_SLA_xử_lý_cảnh_báo_AML|KS-007 - Theo dõi SLA xử lý cảnh báo AML]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: theo dõi SLA giảm nguy cơ báo cáo muộn"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-007_Báo_cáo_giao_dịch_đáng_ngờ_nộp_quá_hạn_n|SK-007 - Báo cáo giao dịch đáng ngờ nộp quá hạn nội bộ]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện báo cáo AML muộn"
