# 🔐 BUỔI 15: CÀI ĐẶT KIỂM SOÁT TRUY CẬP (RBAC) CHO RAG PIPELINE & KNOWLEDGE GRAPH

## 📌 Tổng quan dự án
Dự án đã triển khai cơ chế **Role-Based Access Control (RBAC)** đa tầng:
- **Tầng dữ liệu (Data-level Security):** Gắn thẻ allowed_roles cho 1.295 chunks.
- **Tầng đồ thị (Secure Graph Neo4j):** Cập nhật thuộc tính mảng allowed_roles lên các Node VanBan và DieuKhoan.
- **Tầng Retrieval (Secure Retriever):** Lọc quyền truy cập nghiêm ngặt trước khi đưa vào Cross-Encoder Reranker, ngăn chặn 100% rò rỉ dữ liệu.
- **Tầng Ứng dụng (Streamlit App RBAC):** Cho phép đóng vai (Impersonate) các vai trò Admin, HR, Risk_Manager, Staff, Guest.

---

## 📸 Hình ảnh minh chứng kết quả thực hành (Evidence)

### 1. Giao diện trải nghiệm tìm kiếm an toàn phân quyền RBAC
![RBAC Streamlit App](./images/rbac_streamlit.png)

---

### 2. Báo cáo kiểm định an toàn tự động (Security Audit)
Toàn bộ 5/5 Test Cases kiểm thử chống rò rỉ dữ liệu đạt chứng nhận **PASS 100%**:

![Security Audit](./images/security_audit.png)

---

### 3. Đồ thị tri thức gán thẻ bảo mật trên Neo4j
![Neo4j Secure Graph](./images/neo4j_secure.png)

---

## 🚀 Hướng dẫn chạy thử nghiệm
- Chạy ứng dụng bảo mật Streamlit: streamlit run app_secure.py
- Chạy kiểm thử an toàn tự động: python scripts/security_audit.py
