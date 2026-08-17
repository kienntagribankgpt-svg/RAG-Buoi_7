import sys
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="RAG RBAC Secure Search — Buổi 15", page_icon="🔐", layout="wide")

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_15")
sys.path.append(str(base_dir))

from src.secure_retriever import SecureRetriever
from src.config import ROLES

@st.cache_resource
def load_secure_pipeline():
    corpus_file = base_dir / "data" / "processed" / "chunks_secure.csv"
    retriever = SecureRetriever(corpus_file, cache_dir=base_dir / "cache")
    return retriever

retriever = load_secure_pipeline()

st.title("🔐 RAG Secure Retrieval với Phân Quyền RBAC — Buổi 15")
st.markdown("Hệ thống Tìm kiếm Lai có kiểm soát truy cập dựa trên vai trò ở mức dữ liệu và đồ thị")

with st.sidebar:
    st.header("👤 Đóng vai (Impersonate Role)")
    user_roles = st.multiselect(
        "Chọn vai trò hiện tại của bạn (Your Roles):",
        options=ROLES,
        default=["Staff"]
    )
    
    st.markdown("---")
    st.header("⚙️ Cấu hình Retrieval")
    method = st.selectbox("Phương thức Retrieval:", ["Hybrid + Rerank", "Hybrid", "Dense (Vector)", "BM25 (Từ khóa)"])
    top_k = st.slider("Top-K hiển thị:", min_value=1, max_value=10, value=5)
    
    st.markdown("---")
    st.subheader("💡 Câu hỏi thử nghiệm RBAC")
    sample_queries = [
        "Thành lập Hội đồng đầu tư quỹ liên kết đơn vị doanh nghiệp bảo hiểm (Mật - HR/Admin)",
        "Quy định về thẩm quyền phê duyệt và hạn mức cho vay? (Mật - Risk/Staff/Admin)",
        "Quy định niêm phong tiền mặt theo Điều 5 Thông tư 01/2014/TT-NHNN (Công khai - Mọi Role)"
    ]
    chosen = st.selectbox("Chọn câu hỏi mẫu:", ["-- Tự nhập câu hỏi --"] + sample_queries)

if chosen != "-- Tự nhập câu hỏi --":
    query_val = chosen.split(" (")[0]
else:
    query_val = "Thành lập Hội đồng đầu tư quỹ liên kết đơn vị doanh nghiệp bảo hiểm"

query = st.text_input("🔑 Nhập câu hỏi truy vấn:", value=query_val)

if st.button("🚀 Thực hiện tìm kiếm an toàn", type="primary"):
    if not user_roles:
        st.error("⛔ Bạn chưa chọn vai trò người dùng nào ở Sidebar! Vui lòng chọn ít nhất 1 vai trò.")
    else:
        with st.spinner("Đang thực hiện lọc quyền và truy xuất an toàn..."):
            retrieval_method = "hybrid_rerank" if method == "Hybrid + Rerank" else "hybrid" if method == "Hybrid" else "dense" if method == "Dense (Vector)" else "bm25"
            results, filtered_count = retriever.retrieve(query, user_roles=user_roles, method=retrieval_method, top_k=top_k)
            
        st.info(f"🛡️ **Trạng thái phân quyền:** Đang đóng vai: `{user_roles}` | 🚫 **Đã lọc bỏ an toàn {filtered_count} đoạn văn bản** do không đủ quyền truy cập.")
        
        if not results:
            st.warning("⚠️ Không tìm thấy kết quả nào phù hợp trong phạm vi quyền hạn của bạn.")
        else:
            st.subheader(f"📋 Kết quả được phép truy cập ({len(results)} kết quả)")
            
            for r in results:
                rank = r.get("final_rank", r.get("rank", 1))
                score = r.get("rerank_score", r.get("rrf_score", r.get("retrieval_score", 0.0)))
                roles_str = ", ".join(r.get("allowed_roles", []))
                
                with st.expander(f"Top {rank}: {r['chunk_id']} | Điểm: {score:.4f} | 🔒 Quyền xem: [{roles_str}]", expanded=True):
                    st.markdown(f"**Nguồn trích dẫn (Citation):** `{r.get('citation', '')}`")
                    st.success(r.get("text", ""))
                    
            st.markdown("---")
            st.subheader("🌐 Secure Graph Hints (Đồ thị tri thức an toàn)")
            docs_accessible = list(set([r["document_id"] for r in results]))
            st.write(f"- Các văn bản trong phạm vi được xem: `{docs_accessible}`")
            st.write(f"- Mệnh đề bảo mật Cypher tương ứng: `WHERE any(role IN node.allowed_roles WHERE role IN {user_roles})`")
