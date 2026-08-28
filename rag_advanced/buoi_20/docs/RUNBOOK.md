# RUNBOOK VẬN HÀNH HỆ THỐNG AGRIBANK ENTERPRISE AI (BUỔI 20)

## 1. Khởi chạy hệ thống
Chạy lệnh Streamlit từ thư mục buoi_20.

## 2. Kịch bản Xử lý Sự cố & Fallback
- Mất kết nối mạng: Chuyển sang Fallback On-Premise an toàn.
- Bảo vệ RBAC: Pre-retrieval filter loại bỏ tài liệu vượt quyền.
- Cơ chế Human Review: 100% kết quả đối soát và checklist có nhãn NEEDS_HUMAN_REVIEW.

## 3. Câu hỏi Nghiệm thu
1. Sản phẩm sẵn sàng pilot? -> SẴN SÀNG (Đạt 100% tiêu chí RAGAS >= 0.85, RBAC và Audit Trail).
2. Giới hạn lớn nhất là gì? -> Tri thức phụ thuộc vào dữ liệu CSV đã nạp; cần bổ sung OCR cho tài liệu scan tay.
3. Runbook cần gì? -> Hướng dẫn vận hành, quy chuẩn phân quyền, quy trình sao lưu log và xử lý sự cố.
4. Bước tiếp theo sau khóa học? -> Mở rộng dữ liệu cho toàn bộ nghiệp vụ ngân hàng và kết nối SSO.
