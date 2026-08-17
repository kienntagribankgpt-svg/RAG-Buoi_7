import sys
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="RAG Hybrid Search — Buổi 14", page_icon="🔍", layout="wide")

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_15")
sys.path.append(str(base_dir))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever
from src.reranker import Reranker

@st.cache_resource
def load_pipeline():
    corpus_file = base_dir / "data" / "processed" / "chunks_normalized.csv"
    df_corpus = pd.read_csv(corpus_file)
    bm25 = BM25Retriever(df_corpus)
    dense = DenseRetriever(df_corpus, cache_dir=base_dir / "cache")
    hybrid = HybridRetriever(bm25, dense)
    reranker = Reranker()
    return bm25, dense, hybrid, reranker, df_corpus

bm25, dense, hybrid, reranker, df_corpus = load_pipeline()

# Giao diện chính
st.title("🔍 RAG Hybrid Search — Buổi 14")
st.markdown("Hệ thống Tìm kiếm Lai (Hybrid Lexical + Dense) kết hợp Neural Cross-Encoder Reranking & Knowledge Graph Hints")

# Sidebar cấu hình
with st.sidebar:
    st.header("⚙️ Cấu Hình Tìm Kiếm")
    method = st.selectbox("Phương thức Retrieval (Method):", ["Hybrid + Rerank", "So sánh cả 4 Mô hình (Compare All)", "Hybrid", "Dense (Vector)", "BM25 (Từ khóa)"])
    candidate_k = st.slider("Số lượng Candidate-K (Ứng viên):", min_value=5, max_value=30, value=15)
    top_k = st.slider("Số lượng Top-K hiển thị:", min_value=1, max_value=10, value=5)
    
    st.markdown("---")
    st.subheader("💡 Câu hỏi gợi ý")
    example_queries = [
        "Quy định niêm phong tiền mặt theo Điều 5 Thông tư 01/2014/TT-NHNN",
        "Điều kiện vay vốn và các nhu cầu vốn không được cho vay được quy định như thế nào?",
        "Thẩm quyền phê duyệt cấp tín dụng và hạn mức cho vay?",
        "Thành lập Hội đồng đầu tư quỹ liên kết đơn vị doanh nghiệp bảo hiểm"
    ]
    selected_example = st.selectbox("Chọn câu hỏi mẫu:", ["-- Tự nhập câu hỏi --"] + example_queries)

if selected_example != "-- Tự nhập câu hỏi --":
    query_input_val = selected_example
else:
    query_input_val = "Quy định niêm phong tiền mặt theo Điều 5 Thông tư 01/2014/TT-NHNN"

query = st.text_input("🔑 Câu hỏi truy vấn:", value=query_input_val)

if st.button("🚀 Tìm kiếm", type="primary"):
    with st.spinner("Đang thực hiện truy xuất và xếp hạng..."):
        # Lấy kết quả từ các nhánh
        bm25_cands = bm25.retrieve(query, top_k=candidate_k)
        dense_cands = dense.retrieve(query, top_k=candidate_k)
        hyb_cands = hybrid.retrieve(query, top_k=candidate_k, candidate_k=candidate_k)
        rerank_results = reranker.rerank(query, hyb_cands, top_k=top_k)

    # 1. Chế độ SO SÁNH CẢ 4 MÔ HÌNH
    if method == "So sánh cả 4 Mô hình (Compare All)":
        st.subheader("📊 BẢNG SO SÁNH KẾT QUẢ CỦA 4 MÔ HÌNH RETRIEVAL")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 Hybrid + Rerank", "⚡ Hybrid (RRF)", "🎯 Dense (Vector)", "🔤 BM25 (Từ khóa)"])
        
        with tab1:
            st.markdown(f"**Top {top_k} kết quả sau khi Cross-Encoder chấm điểm lại:**")
            for r in rerank_results:
                st.info(f"**Rank {r['final_rank']}** | Chunk: `{r['chunk_id']}` | Rerank Score: `{r.get('rerank_score', 0):.4f}`\n\n**Citation:** `{r['citation']}`\n\n{r['text']}")
        with tab2:
            st.markdown(f"**Top {top_k} kết quả kết hợp RRF:**")
            for r in hyb_cands[:top_k]:
                st.success(f"**Rank {r['final_rank']}** | Chunk: `{r['chunk_id']}` | RRF Score: `{r['rrf_score']:.5f}` (BM25 Rank: {r['bm25_rank']}, Dense Rank: {r['dense_rank']})\n\n**Citation:** `{r['citation']}`\n\n{r['text']}")
        with tab3:
            st.markdown(f"**Top {top_k} kết quả theo ngữ nghĩa Dense Embedding:**")
            for r in dense_cands[:top_k]:
                st.warning(f"**Rank {r['rank']}** | Chunk: `{r['chunk_id']}` | Cosine Score: `{r['retrieval_score']:.4f}`\n\n**Citation:** `{r['citation']}`\n\n{r['text']}")
        with tab4:
            st.markdown(f"**Top {top_k} kết quả theo từ khóa BM25:**")
            for r in bm25_cands[:top_k]:
                st.error(f"**Rank {r['rank']}** | Chunk: `{r['chunk_id']}` | BM25 Score: `{r['retrieval_score']:.4f}`\n\n**Citation:** `{r['citation']}`\n\n{r['text']}")

    # 2. Chế độ HYBRID + RERANK (Có bảng Before / After)
    elif method == "Hybrid + Rerank":
        st.subheader(f"📋 Kết Quả Retrieval (Hybrid + Rerank | Top-{top_k})")
        
        st.markdown("### 🔄 BẢNG SO SÁNH THỨ HẠNG (BEFORE / AFTER RERANK)")
        
        table_rows = []
        for r in rerank_results:
            table_rows.append({
                "Final Rank (AFTER)": f"🥇 Rank {r['final_rank']}" if r['final_rank'] == 1 else f"🥈 Rank {r['final_rank']}" if r['final_rank'] == 2 else f"🥉 Rank {r['final_rank']}" if r['final_rank'] == 3 else f"Rank {r['final_rank']}",
                "Hybrid Rank (BEFORE)": f"Rank {r.get('final_rank_before', r.get('rank', '-'))}",
                "Rerank Score": f"{r.get('rerank_score', 0):.4f}",
                "Hybrid RRF Score": f"{r.get('rrf_score', 0):.6f}",
                "Chunk ID": r["chunk_id"],
                "Article / Title": r.get("citation", "").split("|")[1].strip() if "|" in r.get("citation", "") else r["chunk_id"]
            })
            
        st.table(pd.DataFrame(table_rows))
        
        st.markdown("---")
        st.markdown("### 📑 Chi tiết nội dung các đoạn văn bản (Chunks):")
        for r in rerank_results:
            with st.expander(f"Top {r['final_rank']} | {r['chunk_id']} | Điểm Rerank: {r.get('rerank_score', 0):.4f}", expanded=True):
                st.markdown(f"**Nguồn trích dẫn (Citation):** `{r['citation']}`")
                st.write(r["text"])

    else:
        # Các chế độ đơn lẻ khác
        current_res = bm25_cands if method == "BM25 (Từ khóa)" else dense_cands if method == "Dense (Vector)" else hyb_cands
        st.subheader(f"📋 Kết Quả Retrieval ({method} | Top-{top_k})")
        for r in current_res[:top_k]:
            rank = r.get("final_rank", r.get("rank"))
            score = r.get("rrf_score", r.get("retrieval_score", 0.0))
            with st.expander(f"Top {rank}: {r['chunk_id']} | Score: {score:.4f}", expanded=True):
                st.markdown(f"**Citation:** `{r['citation']}`")
                st.write(r["text"])

    # Graph hints phần chân trang
    st.markdown("---")
    st.subheader("🌐 Knowledge Graph Hints")
    docs_found = list(set([r["document_id"] for r in rerank_results]))
    st.info(f"📌 **Văn bản liên quan trực tiếp được kích hoạt trong Graph:** `{docs_found}`\n\n"
            f"🔗 **Mô hình liên kết trong Neo4j:** `(:VanBan {{id: '{docs_found[0]}' }})-[:CONTAINS]->(:DieuKhoan)-[:NEXT]->(:DieuKhoan)`")
