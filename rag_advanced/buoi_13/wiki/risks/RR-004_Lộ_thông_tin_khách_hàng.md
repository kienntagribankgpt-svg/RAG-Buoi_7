---
id: RR-004
type: RuiRo
name: "Lộ thông tin khách hàng"
category: "Rui ro cong nghe thong tin"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-IT"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-004 - Lộ thông tin khách hàng

## 1. Mô tả & Diễn biến
- **Mô tả:** Quyền truy cập dữ liệu không được kiểm soát phù hợp
- **Nguyên nhân (Cause):** Cấp quyền vượt nhu cầu công việc
- **Sự kiện kích hoạt (Event):** Dữ liệu khách hàng bị truy cập hoặc chia sẻ trái phép
- **Hậu quả & Tác động (Impact):** Vi phạm bảo mật và tổn hại uy tín

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-004_Rà_soát_quyền_truy_cập_định_kỳ|KS-004 - Rà soát quyền truy cập định kỳ]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: rà soát quyền hạn giảm lộ dữ liệu"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-004_Tài_khoản_có_quyền_truy_cập_dữ_liệu_vượt|SK-004 - Tài khoản có quyền truy cập dữ liệu vượt phạm vi công việc]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện quyền truy cập quá mức"
