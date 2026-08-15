---
id: RR-005
type: RuiRo
name: "Gián đoạn dịch vụ ngân hàng số"
category: "Rui ro cong nghe thong tin"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-IT"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-005 - Gián đoạn dịch vụ ngân hàng số

## 1. Mô tả & Diễn biến
- **Mô tả:** Hệ thống thanh toán trực tuyến không sẵn sàng
- **Nguyên nhân (Cause):** Kế hoạch năng lực và dự phòng chưa đầy đủ
- **Sự kiện kích hoạt (Event):** Dịch vụ ngân hàng số bị gián đoạn
- **Hậu quả & Tác động (Impact):** Mất doanh thu và khiếu nại khách hàng

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-005_Kiểm_thử_khả_năng_chịu_tải_và_chuyển_đổi|KS-005 - Kiểm thử khả năng chịu tải và chuyển đổi dự phòng]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: kiểm thử dự phòng giảm gián đoạn dịch vụ"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-005_Dịch_vụ_ngân_hàng_số_gián_đoạn_trong_giờ|SK-005 - Dịch vụ ngân hàng số gián đoạn trong giờ cao điểm]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện gián đoạn dịch vụ"
