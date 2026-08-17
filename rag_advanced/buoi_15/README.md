# 🔐 BUỔI 15: CÀI ĐẶT KIỂM SOÁT TRUY CẬP (RBAC) CHO RAG PIPELINE & KNOWLEDGE GRAPH

## 📌 Tổng quan tính năng bảo mật
Dự án đã triển khai cơ chế **Role-Based Access Control (RBAC)** đa tầng:
- **Tầng dữ liệu (Data-level Security):** Gắn thẻ `allowed_roles` cho 1.295 chunks (`chunks_secure.csv`).
- **Tầng đồ thị (Secure Graph Neo4j):** Cập nhật thuộc tính mảng `allowed_roles` lên các Node `VanBan` và `DieuKhoan`.
- **Tầng Retrieval (Secure Retriever):** Lọc quyền truy cập nghiêm ngặt trước khi đưa vào Cross-Encoder Reranker, ngăn chặn 100% rò rỉ dữ liệu.
- **Tầng Ứng dụng (Streamlit App RBAC):** Cho phép đóng vai (Impersonate) các vai trò `Admin`, `HR`, `Risk_Manager`, `Staff`, `Guest`.

---

## 📸 Hình ảnh minh chứng kiểm thử RBAC

### 1. Vai trò Guest bị chặn truy cập tài liệu mật (No Data Leakage)
![RBAC Guest Blocked](./images/rbac_guest_blocked.png)

---

### 2. Vai trò HR / Admin truy cập thành công tài liệu được phân quyền
![RBAC Authorized](./images/rbac_admin_authorized.png)

---

## 📊 Kết quả kiểm toán bảo mật tự động (Security Integration Audit)
Toàn bộ 5/5 Test Case đạt **PASS 100%** (Xem chi tiết tại `outputs/security_audit_report.md`).