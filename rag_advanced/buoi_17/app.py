import json
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

base_dir = Path(r"D:/du_an_cua_ban/RAG/rag_advanced/buoi_17")
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from scripts.internal_lookup import internal_lookup
from scripts.compliance_gap import run_compliance_gap_analysis

st.set_page_config(page_title="Secure RAG & Compliance — Buổi 17", page_icon="🏦", layout="wide")

# Header Cảnh báo Kiểm toán & Title
st.warning("⚠️ **Demo Đào tạo** — Kết quả đối soát AI chỉ mang tính tham khảo và bắt buộc phải được Kiểm toán viên xác minh trước khi phát hành kết luận.")
st.title("🏦 Secure RAG, Audit Trail & AI Compliance Gap Checker — Buổi 17")

# Sidebar: Phân quyền RBAC
st.sidebar.header("👤 Thông tin Định danh & Phân quyền")
user_id = st.sidebar.text_input("User ID Demo:", value="kiemtoan_01")
role = st.sidebar.selectbox("User Role:", ["KiemToanVien", "Admin", "Risk_Manager", "HR", "Staff", "Guest"])
st.sidebar.info(f"**Quyền hiện tại**: `{role}`\n\nCơ chế RBAC lọc trước khi gửi dữ liệu vào LLM Context.")

# 3 Tabs theo đúng kịch bản nghiệp vụ
tab1, tab2, tab3 = st.tabs(["🔍 1. TRA CỨU QUY ĐỊNH NỘI BỘ", "⚖️ 2. AI COMPLIANCE GAP CHECKER", "📜 3. AUDIT TRAIL LOGS"])

# --- TAB 1: TRA CỨU QUY ĐỊNH NỘI BỘ ---
with tab1:
    st.subheader("Use Case 1: Tra cứu Quy định có Phân quyền (RBAC)")
    sample_queries = [
        "-- Tự nhập câu hỏi --",
        "Quy định về niêm phong tiền mặt theo Thông tư 01/2014/TT-NHNN?",
        "Thẩm quyền quyết định phê duyệt cấp tín dụng thuộc về ai?",
        "Chính sách thù lao và tiền lương cho cán bộ kiểm toán nội bộ?",
        "Quy trình bổ nhiệm cán bộ quản lý quỹ đầu tư?"
    ]
    selected_query = st.selectbox("Chọn câu hỏi mẫu:", sample_queries)
    user_query = st.text_input("Hoặc nhập câu hỏi tra cứu:", value="" if selected_query.startswith("--") else selected_query)
    
    col_k, col_btn = st.columns([1, 4])
    with col_k:
        top_k = st.slider("Top-k hiển thị:", 1, 5, 3)
    with col_btn:
        st.write("")
        st.write("")
        run_btn = st.button("🚀 Thực hiện Tra cứu An toàn", use_container_width=True)
        
    if run_btn and user_query.strip():
        with st.spinner("Đang thực hiện RBAC Filtering và Hybrid Search..."):
            res = internal_lookup(user_query, user_role=role, user_id_demo=user_id, top_k=top_k)
            if res["access_decision"] == "ALLOWED":
                st.success(f"**Quyết định truy cập:** ✅ `{res['access_decision']}` | **Request ID:** `{res['request_id']}`")
                st.markdown(f"### 💡 Câu trả lời:\n{res['answer']}")
                with st.expander("📚 Chi tiết Tài liệu & Trích dẫn Nguồn (Citations):", expanded=True):
                    for d in res["retrieved_docs"]:
                        st.markdown(f"- **Rank {d['rank']}**: `{d['citation']}` (Document: `{d['document_id']}` | Role: `{d['allowed_roles']}`)")
                        st.caption(d["text"])
            else:
                st.error(f"**Quyết định truy cập:** ⛔ `{res['access_decision']}` | **Request ID:** `{res['request_id']}`")
                st.warning("Bạn không có quyền truy cập vào nội dung tài liệu này hoặc tài liệu đã bị bộ lọc RBAC loại bỏ hoàn toàn.")

# --- TAB 2: AI COMPLIANCE GAP CHECKER ---
with tab2:
    st.subheader("Use Case 2: AI Compliance Gap Checker (NHNN vs Quy định Nội bộ)")
    st.markdown("Hệ thống tự động so sánh yêu cầu từ Thông tư NHNN với các bằng chứng thực tế từ quy định nội bộ ngân hàng.")
    if st.button("🔄 Chạy Phân tích & Đối soát Toàn diện"):
        with st.spinner("Đang trích xuất Evidence 2 phía và lập luận AI..."):
            df_gap = run_compliance_gap_analysis(user_role=role, user_id_demo=user_id)
            st.dataframe(df_gap[["gap_id", "external_document_id", "classification", "confidence", "review_status", "request_id"]], use_container_width=True)
            
    gap_csv = base_dir / "outputs" / "compliance_gap_results.csv"
    if gap_csv.exists():
        df_gap_view = pd.read_csv(gap_csv)
        st.markdown("#### Chi tiết các Findings đối soát:")
        for _, row in df_gap_view.iterrows():
            with st.expander(f"📌 {row['gap_id']} | {row['external_document_id']} ➔ Phân loại: {row['classification']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**📜 Yêu cầu NHNN (External):**")
                    st.write(row["external_requirement"])
                    st.caption(f"Trích dẫn: {row['external_citation']}")
                with c2:
                    st.markdown("**🏢 Bằng chứng Nội bộ (Internal):**")
                    st.write(row["internal_evidence"])
                    st.caption(f"Trích dẫn: {row['internal_citation']}")
                st.info(f"**Lập luận AI:** {row['reason']}\n\n**Độ tin cậy:** `{float(row['confidence'])*100:.1f}%` | **Trạng thái kiểm định:** `{row['review_status']}`")

# --- TAB 3: AUDIT TRAIL LOGS ---
with tab3:
    st.subheader("Use Case 3: Nhật ký Truy vết (Audit Trail Logs)")
    log_file = base_dir / "outputs" / "audit_log.jsonl"
    if log_file.exists():
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs[["timestamp_utc", "request_id", "user_id_demo", "user_role", "action", "status", "denied_candidates_count"]], use_container_width=True)
            st.markdown("#### Sự kiện JSON chi tiết gần nhất:")
            st.json(logs[-1])