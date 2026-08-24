import json
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

base_dir = Path(r"D:/du_an_cua_ban/RAG/rag_advanced/buoi_18")
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from scripts.compliance_checker import run_compliance_checker
from scripts.audit_checklist_gen import generate_audit_checklist

st.set_page_config(page_title="AI Compliance & Audit Checklist — Buổi 18", page_icon="🏦", layout="wide")

st.warning("⚠️ **Demo Đào tạo Kiểm toán AI** — Kết quả đối soát và checklist AI chỉ mang tính tham khảo. Kiểm toán viên bắt buộc phải thẩm định trước khi phát hành báo cáo.")
st.title("🏦 AI Compliance Checker & Audit Checklist Generator — Buổi 18")

st.sidebar.header("👤 Định danh & Phân quyền (RBAC)")
user_id = st.sidebar.text_input("User ID Demo:", value="kiemtoan_01")
role = st.sidebar.selectbox("User Role:", ["KiemToanVien", "Admin", "Risk_Manager", "HR", "Staff", "Guest"])
st.sidebar.info(f"**Vai trò:** `{role}`\nCơ chế RBAC kiểm soát phạm vi văn bản trước khi xử lý.")

tab1, tab2, tab3 = st.tabs(["⚖️ 1. UC3 - AI COMPLIANCE CHECKER", "📋 2. UC4 - AUDIT CHECKLIST GEN", "📜 3. AUDIT TRAIL LOGS"])

with tab1:
    st.subheader("UC3: So sánh Chéo & Phát hiện Xung đột Quy định")
    domain_sel = st.selectbox("Chọn Miền nghiệp vụ cần đối soát:", [
        "Tất cả",
        "An toàn kho quỹ & Vận chuyển tiền",
        "Quản lý CAR & Tỷ lệ an toàn",
        "Phân quyền phê duyệt tín dụng"
    ])
    
    if st.button("🚀 Quét Xung đột & So sánh Chéo", use_container_width=True):
        with st.spinner("Đang truy xuất và đối chiếu cặp quy định..."):
            df_res = run_compliance_checker(domain_sel, user_role=role, user_id=user_id)
            if df_res.empty:
                st.error("⛔ Quyền truy cập bị từ chối hoặc không tìm thấy dữ liệu phù hợp.")
            else:
                st.success(f"✅ Phát hiện {len(df_res)} điểm cần lưu ý đối soát!")
                for _, row in df_res.iterrows():
                    sev_color = "🔴" if row["severity"] == "HIGH" else ("🟡" if row["severity"] == "MEDIUM" else "🟢")
                    with st.expander(f"{sev_color} {row['conflict_id']} | {row['domain']} — {row['conflict_type']} [Mức độ: {row['severity']}]"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**📜 Văn bản A ({row['doc_a_id']}):**")
                            st.write(row["doc_a_text"])
                            st.caption(f"Trích dẫn: `{row['doc_a_citation']}`")
                        with c2:
                            st.markdown(f"**🏢 Văn bản B ({row['doc_b_id']}):**")
                            st.write(row["doc_b_text"])
                            st.caption(f"Trích dẫn: `{row['doc_b_citation']}`")
                        st.info(f"**Phân tích của AI:** {row['description']}\n\n**Trạng thái:** `{row['review_status']}` | **Request ID:** `{row['request_id']}`")

with tab2:
    st.subheader("UC4: Tự động Sinh Danh mục Checklist Kiểm toán")
    c_dom, c_unit = st.columns(2)
    with c_dom:
        chk_domain = st.selectbox("Miền kiểm toán:", [
            "Tất cả",
            "An toàn kho quỹ & Vận chuyển tiền",
            "Bảo mật CNTT & AI",
            "Phân quyền phê duyệt tín dụng"
        ])
    with c_unit:
        chk_unit = st.selectbox("Đơn vị được kiểm toán:", [
            "Chi nhánh loại 1",
            "Phòng Giao dịch",
            "Khối CNTT / Trung tâm Dữ liệu",
            "Phòng Khách hàng Doanh nghiệp"
        ])
        
    if st.button("📝 Sinh Checklist Kiểm toán Tự động", use_container_width=True):
        with st.spinner("AI đang tổng hợp căn cứ và xây dựng câu hỏi kiểm toán..."):
            df_chk = generate_audit_checklist(chk_domain, chk_unit, user_role=role, user_id=user_id)
            if df_chk.empty:
                st.error("⛔ Quyền truy cập bị từ chối hoặc không thể sinh checklist cho role hiện tại.")
            else:
                st.success(f"✅ Đã tạo thành công {len(df_chk)} mục kiểm tra!")
                st.dataframe(df_chk[["item_id", "domain", "audit_question", "risk_level", "source_citation", "review_status"]], use_container_width=True)
                for _, r in df_chk.iterrows():
                    with st.expander(f"📌 {r['item_id']}: {r['audit_question']}"):
                        st.markdown(f"**Rủi ro tiềm ẩn:** {r['risk_description']}")
                        st.markdown(f"**Mức rủi ro:** `{r['risk_level']}` | **Căn cứ pháp lý:** `{r['source_citation']}`")
                        st.markdown(f"**Khuyến nghị thực hiện:** {r['recommendation']}")

with tab3:
    st.subheader("UC3 & UC4: Nhật ký Truy vết Kiểm toán (Audit Trail Logs)")
    log_file = base_dir / "outputs" / "audit_log.jsonl"
    if log_file.exists():
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        if logs:
            df_l = pd.DataFrame(logs)
            st.dataframe(df_l[["timestamp_utc", "request_id", "user_id_demo", "user_role", "action", "status"]], use_container_width=True)
            st.markdown("#### Sự kiện JSON chi tiết gần nhất:")
            st.json(logs[-1])
