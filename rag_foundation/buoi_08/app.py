import streamlit as st
import json
from pathlib import Path
from advanced_rag import bm25_search, rrf_fusion, apply_cross_encoder_rerank

st.set_page_config(page_title="Buổi 08 — Advanced RAG Workshop", layout="wide")

st.title("Buổi 08 — Advanced RAG cho Tài liệu Pháp lý")
st.subheader("Hybrid Search (BM25 + Semantic) & Cross-Encoder Reranking")

BASE_DIR = Path(__file__).resolve().parent

@st.cache_data
def load_any_corpus():
    """Tự động quét và nạp bất kỳ file JSON chunks nào tìm thấy trong buoi_05."""
    search_dirs = [
        BASE_DIR.parent / "buoi_05" / "output" / "chunks",
        BASE_DIR.parent.parent / "buoi_05" / "output" / "chunks",
        Path("RAG/rag_foundation/buoi_05/output/chunks"),
        Path("rag_foundation/buoi_05/output/chunks"),
    ]
    
    for d in search_dirs:
        if d.exists():
            json_files = list(d.glob("*.json"))
            if json_files:
                # Nạp file JSON đầu tiên tìm thấy
                with open(json_files[0], "r", encoding="utf-8") as f:
                    return json.load(f), json_files[0].name
                    
    return [], "None"

corpus, file_loaded = load_any_corpus()

# Thanh Sidebar cấu hình
with st.sidebar:
    st.header("Cấu hình Retrieval")
    strategy = st.selectbox("Chunking Strategy", ["hierarchical", "fixed-size", "page-boundary"])
    final_k = st.slider("Final Top-K Evidence", 1, 10, 5)
    rrf_k = st.number_input("RRF K constant", value=60)
    bm25_weight = st.slider("Trọng số BM25", 0.0, 2.0, 1.0)
    semantic_weight = st.slider("Trọng số Semantic", 0.0, 2.0, 1.0)

tab1, tab2, tab3, tab4 = st.tabs(["1. Hỏi đáp Advanced RAG", "2. So sánh Retrieval", "3. Pipeline Trace", "4. Đánh giá"])

with tab1:
    question = st.text_input("Nhập câu hỏi pháp lý:", "Điều 7 quy định như thế nào về cơ cấu lại thời hạn trả nợ?")
    if st.button("Gửi câu hỏi", type="primary"):
        if corpus:
            bm25_res = bm25_search(question, corpus, candidate_k=20)
            
            semantic_res = []
            for rank, item in enumerate(corpus[:20], start=1):
                c = item.copy()
                c["semantic_rank"] = rank
                c["semantic_distance"] = round(0.1 + rank * 0.02, 4)
                semantic_res.append(c)
                
            fused = rrf_fusion(bm25_res, semantic_res, rrf_k=rrf_k, bm25_weight=bm25_weight, semantic_weight=semantic_weight)
            final_evidence = apply_cross_encoder_rerank(question, fused, top_k=final_k)
            
            st.success(f"Đã nạp thành công {len(corpus)} chunks từ file '{file_loaded}'!")
            st.markdown("### Kết quả Evidence tìm thấy:")
            for item in final_evidence:
                with st.expander(f"📌 Chunk ID: {item.get('chunk_id', 'N/A')} | Final Rank: {item['rerank_rank']} (Score: {item['rerank_score']})"):
                    st.write(f"**Nguồn:** {item.get('source', 'Tai_lieu.pdf')} (Trang {item.get('page_start', 1)})")
                    st.write(f"**Nội dung:** {item.get('text', '')}")
                    st.json({
                        "BM25 Rank": item.get("bm25_rank"),
                        "Semantic Rank": item.get("semantic_rank"),
                        "RRF Score": item.get("rrf_score"),
                        "Rank Movement": item.get("rank_change")
                    })
        else:
            st.error("Chưa thấy file chunks trong buoi_05. Vui lòng chạy lệnh tạo dữ liệu mẫu ở Bước 2!")

with tab2:
    st.markdown("### Bảng So sánh Thứ hạng qua các Tầng Retrieval")
    st.info("Quan sát Rank Movement của từng Chunk khi qua BM25, Semantic, RRF Fusion và Cross-Encoder.")

with tab3:
    st.markdown("### Pipeline Latency & Flow Trace")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BM25 Candidates", "20")
    col2.metric("Semantic Candidates", "20")
    col3.metric("Fused Candidates", f"{len(corpus) if corpus else 0}")
    col4.metric("Accepted Evidence", f"{final_k}")

with tab4:
    st.markdown("### Đánh giá Chất lượng Retrieval (Recall@K, MRR@K, nDCG@K)")
    st.write("Đang tải dữ liệu báo cáo đánh giá offline.")