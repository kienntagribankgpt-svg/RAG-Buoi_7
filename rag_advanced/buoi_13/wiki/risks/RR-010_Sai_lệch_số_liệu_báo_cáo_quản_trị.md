---
id: RR-010
type: RuiRo
name: "Sai lệch số liệu báo cáo quản trị"
category: "Rui ro bao cao"
inherent_level: "Trung binh"
residual_level: "Thap"
owner_unit_id: "DV-FINANCE"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-010 - Sai lệch số liệu báo cáo quản trị

## 1. Mô tả & Diễn biến
- **Mô tả:** Dữ liệu nguồn không được đối chiếu
- **Nguyên nhân (Cause):** Thay đổi dữ liệu không có kiểm soát
- **Sự kiện kích hoạt (Event):** Báo cáo quản trị có số liệu sai
- **Hậu quả & Tác động (Impact):** Quyết định quản trị sai lệch

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-010_Đối_chiếu_dữ_liệu_nguồn_trước_khi_phát_h|KS-010 - Đối chiếu dữ liệu nguồn trước khi phát hành báo cáo]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: đối chiếu nguồn giảm sai lệch báo cáo"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-010_Báo_cáo_quản_trị_sử_dụng_dữ_liệu_nguồn_c|SK-010 - Báo cáo quản trị sử dụng dữ liệu nguồn chưa đối chiếu]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện sai lệch báo cáo"
