---
id: RR-006
type: RuiRo
name: "Gian lận giả mạo yêu cầu chuyển tiền"
category: "Rui ro gian lan"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-OPS"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-006 - Gian lận giả mạo yêu cầu chuyển tiền

## 1. Mô tả & Diễn biến
- **Mô tả:** Nhận diện và xác thực yêu cầu chưa đủ mạnh
- **Nguyên nhân (Cause):** Nhân viên không xác minh kênh liên lạc
- **Sự kiện kích hoạt (Event):** Yêu cầu chuyển tiền giả mạo được xử lý
- **Hậu quả & Tác động (Impact):** Tổn thất tài chính

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-006_Xác_thực_hai_kênh_với_lệnh_chuyển_tiền_n|KS-006 - Xác thực hai kênh với lệnh chuyển tiền ngoại lệ]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: xác thực hai kênh giảm gian lận chuyển tiền"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-006_Yêu_cầu_chuyển_tiền_giả_mạo_được_xử_lý_t|SK-006 - Yêu cầu chuyển tiền giả mạo được xử lý trước khi bị thu hồi]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện giả mạo chuyển tiền"
