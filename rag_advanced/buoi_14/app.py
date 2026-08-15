import sys
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="RAG Hybrid Search - Buổi 14", page_icon="🛡️", layout="wide")

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_14")
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

st.title("🛡️ RAG Hybrid Search + Reranking & Mini KG — Buổi 14")
st.caption("Kiến trúc hợp nhất: BM25 (Từ khóa) + Dense Vector (Ngữ nghĩa) + Reranking + Graph Tri thức")

with st.sidebar:
    st.header("⚙️ Cấu hình Retrieval")
    method = st.selectbox("Phương thức Retrieval:", ["Hybrid + Rerank", "Hybrid", "Dense (Vector)", "BM25 (Từ khóa)"])
    top_k = st.slider("Số lượng Top-K kết quả:", min_value=1, max_value=10, value=3)

default_query = "Điều kiện vay vốn và các nhu cầu vốn không được cho vay được quy định như thế nào?"
query = st.text_input("Nhập câu hỏi nghiệp vụ / pháp lý:", value=default_query)

if st.button("🚀 Thực hiện tìm kiếm", type="primary"):
    with st.spinner("Đang truy xuất dữ liệu qua Pipeline..."):
        if method == "BM25 (Từ khóa)":
            results = bm25.retrieve(query, top_k=top_k)
        elif method == "Dense (Vector)":
            results = dense.retrieve(query, top_k=top_k)
        elif method == "Hybrid":
            results = hybrid.retrieve(query, top_k=top_k)
        else:
            cands = hybrid.retrieve(query, top_k=15, candidate_k=15)
            results = reranker.rerank(query, cands, top_k=top_k)
            
    st.subheader(f"📋 Kết quả Retrieval ({method} - Top {top_k})")
    
    docs_set = set()
    for r in results:
        rank = r.get("final_rank", r.get("rank"))
        score = r.get("rerank_score", r.get("rrf_score", r.get("retrieval_score", 0.0)))
        docs_set.add(r["document_id"])
        
        with st.expander(f"Top {rank}: {r['chunk_id']} | Điểm số: {score:.4f}", expanded=True):
            st.markdown(f"**Trích dẫn (Citation):** `{r['citation']}`")
            if "bm25_rank" in r and "dense_rank" in r:
                st.caption(f"BM25 Rank: {r['bm25_rank']} | Dense Rank: {r['dense_rank']}")
            st.info(r["text"])
            
    st.markdown("---")
    st.subheader("🌐 Graph Hints (Mối quan hệ pháp lý đồ thị)")
    st.write(f"- **Văn bản liên quan trực tiếp:** `{list(docs_set)}`")
    st.write("- **Cấu trúc liên kết có sẵn trong Neo4j:** `(:VanBan)-[:CONTAINS]->(:DieuKhoan)-[:NEXT]->(:DieuKhoan)`")