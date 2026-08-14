# BÁO CÁO KẾT QUẢ BUỔI 12: CHUẨN HÓA, LÀM GIÀU METADATA VÀ XÂY DỰNG ĐỒ THỊ TRI THỨC

## 1. Kết quả Pipeline hoàn thành
- [PASS] **Bước 0**: Môi trường, dữ liệu và kết nối Neo4j.
- [PASS] **Bước 1**: Làm sạch HTML, tạo `cleaned_documents.csv`.
- [PASS] **Bước 2**: Trích xuất candidates theo trigger & regex (`relation_candidates.csv`).
- [PASS] **Bước 3**: Entity Extraction & Enrichment (`extracted_entities_raw.csv`, `enriched_metadata.csv`).
- [PASS] **Bước 4**: Chuẩn hóa Entity (`entities.csv`).
- [PASS] **Bước 5 & 6**: Trích xuất & Validate Relationships (`relationships.csv`, `validation_report.csv`).
- [PASS] **Bước 7, 8 & 9**: Nạp thành công vào cơ sở dữ liệu đồ thị Neo4j.

## 2. Hình ảnh minh chứng kết quả

### Màn hình nghiệm thu thành công toàn bộ Pipeline:
![Ket Qua Terminal](./image/loi 12_10.png)

### Các bước thực thi chi tiết:
![Chay Pipeline](./image/loi 12_9.png)