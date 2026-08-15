---
id: RR-009
type: RuiRo
name: "Không phát hiện giao dịch bất thường"
category: "Rui ro gian lan"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-OPS"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-009 - Không phát hiện giao dịch bất thường

## 1. Mô tả & Diễn biến
- **Mô tả:** Luật phát hiện gian lận không được cập nhật
- **Nguyên nhân (Cause):** Ngưỡng cảnh báo không phù hợp
- **Sự kiện kích hoạt (Event):** Giao dịch nghi ngờ không bị chặn kịp thời
- **Hậu quả & Tác động (Impact):** Tổn thất tài chính và uy tín

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-009_Hiệu_chỉnh_luật_phát_hiện_giao_dịch_gian|KS-009 - Hiệu chỉnh luật phát hiện giao dịch gian lận]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: hiệu chỉnh luật giảm bỏ sót giao dịch bất thường"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-009_Giao_dịch_bất_thường_chỉ_bị_phát_hiện_sa|SK-009 - Giao dịch bất thường chỉ bị phát hiện sau khi khách hàng khiếu nại]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện không phát hiện bất thường"
