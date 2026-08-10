import streamlit as st
import json
import sys
from pathlib import Path

# Thêm đường dẫn hiện tại vào sys.path để import module
sys.path.append(str(Path(__file__).resolve().parent))
from hierarchical_rag import run_query_pipeline, expand_query, multi_child_retrieval, parent_retrieval

st.set_page_config(page_title="Buổi 09 — Multi-query & Parent-Child RAG", layout="wide")

st.title("RAG Foundation — Buổi 09: Multi-query & Parent–Child Retrieval")
st.caption("Query fan-out → Hybrid per query → Cross-query RRF → Parent expansion → Parent rerank")

# SIDEBAR
st.sidebar.header("⚙️ Cấu hình Pipeline")
selected_mode = st.sidebar.selectbox("Chế độ Retrieval (Mode)", ["multi_parent", "single_parent", "multi_flat", "single_flat"], index=0)
st.sidebar.slider("MULTI_QUERY_COUNT", 1, 5, 3)
st.sidebar.slider("PER_QUERY_CANDIDATES", 5, 30, 12)
st.sidebar.slider("PARENT_CANDIDATES", 5, 20, 10)
st.sidebar.slider("FINAL_PARENT_TOP_K", 1, 5, 3)
st.sidebar.slider("RERANK_MIN_SCORE", 0.0, 1.0, 0.5)

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask Advanced RAG", "🔀 Query Fan-out", "🌳 Parent–Child Explorer", "📊 Mode Comparison"])

with tab1:
    question = st.text_area("Nhập câu hỏi pháp lý ngân hàng:", "Điều kiện vay vốn và nhu cầu vốn không được cho vay", height=100)
    if st.button("Gửi câu hỏi", type="primary"):
        with st.spinner("Đang xử lý qua pipeline Multi-query & Parent-Child..."):
            res = run_query_pipeline(question, mode=selected_mode)
            st.markdown("### 📝 Câu trả lời")
            st.success(res.get("answer", ""))
            
            st.markdown("### 📚 Nguồn trích dẫn (Citations)")
            for cit in res.get("citations", []):
                st.info(f"**{cit['label']}** - File: `{cit['source']}` ({cit['pages']}) | Anchor Child: `{cit['anchor_child_id']}` | Rerank Score: `{cit['score']}`")

with tab2:
    st.subheader("Truy vấn mở rộng (Query Fan-out)")
    if st.button("Tạo biến thể Query (Fan-out)"):
        q_data = expand_query(question)
        cols = st.columns(len(q_data["queries"]))
        for idx, q in enumerate(q_data["queries"]):
            with cols[idx]:
                st.metric(label=f"Query {q['query_id']}", value=q["focus"])
                st.write(f"**Nội dung:** {q['text']}")

with tab3:
    st.subheader("Cây phân cấp Parent–Child Context")
    if st.button("Khám phá Parent Store"):
        p_data = parent_retrieval(question, mode=selected_mode)
        for cand in p_data.get("parent_candidates", []):
            with st.expander(f"📌 {cand['parent_id']} (Parent Score: {cand['parent_rrf_score']})"):
                st.write(f"**Source:** `{cand['source']}` (Trang {cand['page_start']}-{cand['page_end']})")
                st.write(f"**Anchor Child:** `{cand['anchor_child_id']}`")
                st.text_area("Parent Text (Ngữ cảnh mở rộng):", cand["text"], height=120)

with tab4:
    st.subheader("So sánh trực quan 4 Chế độ Retrieval")
    if st.button("Chạy so sánh 4 Mode"):
        st.dataframe({
            "Mode": ["single_flat", "multi_flat", "single_parent", "multi_parent"],
            "Evidence Unit": ["Child Chunk", "Child Chunk", "Parent Context", "Parent Context"],
            "Query Fan-out": ["Không (Q0)", "Có (Q0..Q3)", "Không (Q0)", "Có (Q0..Q3)"],
            "Rank Fusion": ["Inner RRF", "Cross-Query RRF", "Inner RRF", "Cross-Query RRF"],
            "Reranker Target": ["Child", "Child", "Parent", "Parent"]
        }, use_container_width=True)