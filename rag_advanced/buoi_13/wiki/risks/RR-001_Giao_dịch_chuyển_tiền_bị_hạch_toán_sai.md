---
id: RR-001
type: RuiRo
name: "Giao dịch chuyển tiền bị hạch toán sai"
category: "Rui ro van hanh"
inherent_level: "Cao"
residual_level: "Trung binh"
owner_unit_id: "DV-OPS"
verification_status: "VERIFIED"
data_origin: "SYNTHETIC"
---

# Rủi ro: RR-001 - Giao dịch chuyển tiền bị hạch toán sai

## 1. Mô tả & Diễn biến
- **Mô tả:** Đối soát giao dịch cuối ngày không đầy đủ
- **Nguyên nhân (Cause):** Thiếu đối chiếu giữa hệ thống thanh toán và sổ cái
- **Sự kiện kích hoạt (Event):** Giao dịch được ghi nhận sai trạng thái
- **Hậu quả & Tác động (Impact):** Tổn thất tài chính và khiếu nại khách hàng

## 2. Các biện pháp Kiểm soát giảm thiểu (MITIGATES)
- [[KS-001_Đối_soát_tự_động_giao_dịch_và_sổ_cái|KS-001 - Đối soát tự động giao dịch và sổ cái]]
  - *Quan hệ:* `MITIGATES` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: đối soát tự động giảm nguy cơ hạch toán sai"

## 3. Các Sự kiện rủi ro đã phát sinh (OBSERVED_AS)
- [[SK-001_Sai_lệch_trạng_thái_giao_dịch_được_phát_|SK-001 - Sai lệch trạng thái giao dịch được phát hiện khi đối soát cuối ngày]]
  - *Quan hệ:* `OBSERVED_AS` | *Trạng thái:* `VERIFIED`
  - *Bằng chứng trích dẫn:* "Dữ liệu mô phỏng: sự kiện đối soát giao dịch"
