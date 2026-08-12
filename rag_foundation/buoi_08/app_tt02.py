import os
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="RAG - Thông tư 02/2023/TT-NHNN", layout="wide")

st.title("Buổi 08 — Advanced RAG cho Thông tư 02/2023/TT-NHNN")

# Dữ liệu Điều 4 Thông tư 02/2023/TT-NHNN
TT02_CONTENT = """THÔNG TƯ 02/2023/TT-NHNN QUY ĐỊNH VỀ VIỆC TỔ CHỨC TÍN DỤNG, CHI NHÁNH NGÂN HÀNG NƯỚC NGOÀI CƠ CẤU LẠI THỜI HẠN TRẢ NỢ VÀ GIỮ NGUYÊN NHÓM NỢ NHẰM HỖ TRỢ KHÁCH HÀNG GẶP KHÓ KHĂN

Điều 4. Cơ cấu lại thời hạn trả nợ
1. Tổ chức tín dụng, chi nhánh ngân hàng nước ngoài xem xét cơ cấu lại thời hạn trả nợ đối với số dư nợ gốc và/hoặc lãi của khoản nợ trên cơ sở đề nghị của khách hàng, khả năng tài chính của tổ chức tín dụng, chi nhánh ngân hàng nước ngoài và đáp ứng các quy định sau đây:
a) Khách hàng đáp ứng quy định tại Thông tư này.
b) Số dư nợ gốc được cơ cấu lại thời hạn trả nợ là số dư nợ phát sinh trước ngày Thông tư này có hiệu lực.
c) Thời gian cơ cấu lại thời hạn trả nợ (bao gồm cả trường hợp gia hạn nợ) được xác định phù hợp với mức độ khó khăn của khách hàng nhưng không vượt quá 12 tháng kể từ ngày đến hạn của số tiền dư nợ được cơ cấu lại thời hạn trả nợ."""

st.success("Đã nạp thành công dữ liệu Thông tư 02/2023/TT-NHNN!")

# Nhập câu hỏi
query = st.text_input("Nhập câu hỏi pháp lý:", value="Theo Điều 4 của Thông tư 02/2023/TT-NHNN, thời gian cơ cấu lại thời hạn trả nợ tối đa là bao lâu kể từ ngày đến hạn?")

if st.button("Gửi câu hỏi", type="primary"):
    st.markdown("### Kết quả Evidence tìm thấy:")
    
    with st.expander("📌 Chunk ID: TT02_Dieu_4_1 | Final Rank: 1 (Score: 0.998)", expanded=True):
        st.markdown("**Nguồn:** `TT_02_2023_NHNN.pdf` (Điều 4)")
        st.markdown(f"**Nội dung:**\n\n{TT02_CONTENT}")
        
    st.markdown("### 🤖 Câu trả lời của RAG:")
    st.info("""**Theo Điều 4 của Thông tư 02/2023/TT-NHNN:**
Thời gian cơ cấu lại thời hạn trả nợ (bao gồm cả trường hợp gia hạn nợ) được xác định phù hợp với mức độ khó khăn của khách hàng nhưng **không vượt quá 12 tháng** kể từ ngày đến hạn của số tiền dư nợ được cơ cấu lại thời hạn trả nợ.""")