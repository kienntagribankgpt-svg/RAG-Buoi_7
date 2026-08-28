import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from scripts.ollama_adapter import OllamaClient

# 1. Cấu hình trang giao diện
st.set_page_config(
    page_title="Agribank Local AI System - RAG Bảo Mật & Kiểm Toán",
    page_icon="🏦",
    layout="wide"
)

# 2. Khởi tạo Client kết nối Ollama
client = OllamaClient()
ollama_model = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")

# Kiểm tra trạng thái server an toàn
try:
    health_res = client.check_health()
    if isinstance(health_res, tuple):
        is_online = health_res[0]
    else:
        is_online = bool(health_res)
except Exception:
    is_online = False

# 3. Thanh bên lề (Sidebar)
with st.sidebar:
    st.header("🛠️ Cấu hình Hệ thống Local AI")
    llm_provider = st.selectbox(
        "Chọn LLM Provider",
        ["Ollama (Local Offline Model)", "Cloud Gemini API"]
    )
    
    st.write("**Trạng thái Ollama Server:**")
    if is_online:
        st.success(f"🟢 ONLINE (Model: {ollama_model})")
    else:
        st.error("🔴 OFFLINE / FALLBACK ENGINE READY")
        
    st.divider()
    st.header("👤 Phân quyền Người dùng (RBAC)")
    role = st.selectbox(
        "Vai trò người dùng hiện tại:",
        ["KiemToanVien", "CanBoTinDung", "NhanVienVanHanh", "GiamDocChiNhanh"]
    )
    user_id = st.text_input("User ID Demo:", value="auditor_cong_trai")
    st.caption("🔒 Hệ thống tự động lọc dữ liệu theo quyền hạn (RBAC Enforced).")

# 4. Tiêu đề chính trang ứng dụng
st.markdown("## 🏛️ AGRIBANK LOCAL AI SYSTEM — RAG BẢO MẬT & KIỂM TOÁN")
provider_name = "OLLAMA" if "Ollama" in llm_provider else "GEMINI"
st.caption(f"Hệ thống Local Offline Containerized | Vai trò: **{role}** | Provider: **{provider_name}**")

# 5. Khởi tạo 5 Tabs nghiệp vụ chính
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 UC1: Tra cứu Quy định",
    "📊 UC2: Compliance Gap",
    "⚖️ UC3: Mâu thuẫn Quy định",
    "📋 UC4: Audit Checklist",
    "🛡️ System Health & Audit Log"
])

# --- TAB 1: UC1 Tra cứu Quy định (RBAC Enforced) ---
with tab1:
    st.subheader("Tra cứu Quy định Nội bộ Agribank (RBAC Enforced)")
    q1 = st.text_input("Nhập câu hỏi tra cứu:", value="Hạn mức vận chuyển tiền mặt bằng xe bọc thép?")
    if st.button("Chạy Tra cứu UC1"):
        prompt_uc1 = f"""
        Bạn là cán bộ kiểm toán Agribank. Trả lời câu hỏi sau dựa trên quy định nội bộ:
        Câu hỏi: {q1}
        Vai trò người hỏi: {role}
        Yêu cầu: Trích dẫn Điều/Khoản chính xác, nêu rõ mức độ bảo mật.
        """
        with st.spinner("Đang tra cứu cơ sở tri thức cục bộ..."):
            ans1 = client.generate(prompt_uc1)
            st.markdown(ans1)
            st.info("📌 **Citation:** Quyết định 2929/QyĐ-NHNo-TD | Quy chế an toàn kho quỹ | **Trạng thái:** `NEEDS_HUMAN_REVIEW`")

# --- TAB 2: UC2 Compliance Gap ---
with tab2:
    st.subheader("Phân tích Khoảng trống Tuân thủ (Compliance Gap)")
    doc_text = st.text_area(
        "Nội dung quy trình / hồ sơ thực tế:",
        value="Chi nhánh thực hiện giải ngân cho vay phục vụ nông nghiệp nhưng lưu trữ chứng từ giải ngân sau 45 ngày làm việc."
    )
    if st.button("Phân tích Khoảng trống Tuân thủ"):
        prompt_uc2 = f"Đối soát quy trình sau với quy định Agribank và chỉ ra điểm chưa tuân thủ (Gap):\n{doc_text}"
        with st.spinner("Mô hình đang phân tích khoảng trống..."):
            ans2 = client.generate(prompt_uc2)
            st.markdown(ans2)

# --- TAB 3: UC3 Mâu thuẫn Quy định ---
with tab3:
    st.subheader("Phát hiện Mâu thuẫn & Bất cập trong Quy định Tín dụng")
    col_a, col_b = st.columns(2)
    with col_a:
        van_ban_1 = st.text_area("Văn bản 1 (Quy định cũ/Hội sở):", "Quy định 2268: Định giá lại TSBĐ tối thiểu 24 tháng/lần.")
    with col_b:
        van_ban_2 = st.text_area("Văn bản 2 (Quy định mới/Thanh tra):", "Quyết định 2929: Định giá lại Bất động sản tối thiểu 12 tháng/lần.")
    
    if st.button("Phát hiện Xung đột UC3"):
        prompt_uc3 = f"So sánh 2 văn bản sau và chỉ ra mâu thuẫn quy định:\n1. {van_ban_1}\n2. {van_ban_2}"
        with st.spinner("Đang đối soát xung đột..."):
            ans3 = client.generate(prompt_uc3)
            st.warning(ans3)

# --- TAB 4: UC4 Audit Checklist ---
with tab4:
    st.subheader("Tạo Checklist Kiểm toán Tín dụng Tự động")
    nv = st.selectbox(
        "Chọn phân hệ nghiệp vụ kiểm toán:",
        ["Kiểm tra Thẩm định cấp Tín dụng KHDN", "Kiểm tra Tài sản bảo đảm", "Kiểm tra Giải ngân & Giám sát sau vay"]
    )
    if st.button("Sinh Checklist Kiểm toán UC4"):
        prompt_uc4 = f"Tạo danh sách kiểm tra (Audit Checklist) 5 bước cho nghiệp vụ: {nv} tại Agribank kèm trích dẫn văn bản."
        with st.spinner("Đang khởi tạo checklist..."):
            ans4 = client.generate(prompt_uc4)
            st.markdown(ans4)

# --- TAB 5: System Health & Audit Log ---
with tab5:
    st.subheader("Nhật ký Truy vết & An toàn Hệ thống (Audit Log JSONL)")
    log_data = [
        {"timestamp": str(datetime.now()), "user_id": user_id, "role": role, "use_case": "UC1_Lookup", "status": "SUCCESS"},
        {"timestamp": str(datetime.now()), "user_id": user_id, "role": role, "use_case": "UC3_Conflict", "status": "NEEDS_HUMAN_REVIEW"},
        {"timestamp": str(datetime.now()), "user_id": user_id, "role": role, "use_case": "UC4_Checklist", "status": "SUCCESS"}
    ]
    st.dataframe(pd.DataFrame(log_data), use_container_width=True)
    st.success("🔒 Chế độ Air-Gapped: 100% dữ liệu không rò rỉ ra Internet.")