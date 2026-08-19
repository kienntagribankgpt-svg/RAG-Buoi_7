import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="RAG Evaluation Dashboard — Buổi 16", page_icon="📊", layout="wide")

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_16")
eval_file = base_dir / "data" / "eval" / "evaluation_results.csv"
report_file = base_dir / "outputs" / "ragas_evaluation_report.md"

st.title("📊 RAG Evaluation Dashboard (Ragas) — Buổi 16")
st.markdown("Hệ thống Đánh giá Hiệu năng RAG tự động bằng phương pháp **LLM-as-a-Judge**")

if not eval_file.exists():
    st.warning("⚠️ Chưa tìm thấy file kết quả đánh giá. Vui lòng chạy script evaluate_rag_pipeline.py trước.")
else:
    df = pd.read_csv(eval_file)
    
    # 1. Hiển thị 4 Metrics cốt lõi
    avg_prec = df["context_precision"].mean()
    avg_rec = df["context_recall"].mean()
    avg_faith = df["faithfulness"].mean()
    avg_rel = df["answer_relevancy"].mean()
    ragas_score = (avg_prec + avg_rec + avg_faith + avg_rel) / 4.0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Context Precision", f"{avg_prec:.3f}", delta=">= 0.80")
    col2.metric("Context Recall", f"{avg_rec:.3f}", delta=">= 0.75")
    col3.metric("Faithfulness", f"{avg_faith:.3f}", delta=">= 0.85")
    col4.metric("Answer Relevancy", f"{avg_rel:.3f}", delta=">= 0.80")
    col5.metric("⭐ Ragas Score", f"{ragas_score:.3f}", delta="EXCELLENT" if ragas_score >= 0.85 else "GOOD")
    
    st.markdown("---")
    
    # 2. Bộ lọc và Phân tích chi tiết
    tab1, tab2, tab3 = st.tabs(["📋 Chi tiết 20 Q&A & Điểm số", "📈 Phân tích Usecase & Độ khó", "📄 Báo cáo Kiểm định (.md)"])
    
    with tab1:
        st.subheader("Bảng dữ liệu kết quả chấm điểm từng câu hỏi")
        selected_usecase = st.multiselect("Lọc theo Use Case:", options=df["usecase"].unique(), default=df["usecase"].unique())
        selected_diff = st.multiselect("Lọc theo Độ khó:", options=df["difficulty"].unique(), default=df["difficulty"].unique())
        
        filtered_df = df[(df["usecase"].isin(selected_usecase)) & (df["difficulty"].isin(selected_diff))]
        st.dataframe(filtered_df[["question_id", "question", "context_precision", "context_recall", "faithfulness", "answer_relevancy", "usecase", "difficulty"]], use_container_width=True)
        
        st.markdown("#### Xem chi tiết từng câu hỏi:")
        q_pick = st.selectbox("Chọn câu hỏi để xem câu trả lời của RAG:", df["question_id"] + " - " + df["question"])
        if q_pick:
            q_id = q_pick.split(" - ")[0]
            row_data = df[df["question_id"] == q_id].iloc[0]
            st.info(f"**Câu hỏi:** {row_data['question']}")
            st.success(f"**Đáp án chuẩn (Ground Truth):** {row_data['ground_truth']}")
            st.write(f"**RAG Generator Answer:** {row_data['answer']}")
            
    with tab2:
        st.subheader("Thống kê điểm số trung bình theo phân nhóm")
        col_u, col_d = st.columns(2)
        with col_u:
            st.markdown("**Theo Use Case (Nghiệp vụ):**")
            st.table(df.groupby("usecase")[["context_precision", "context_recall", "faithfulness", "answer_relevancy"]].mean().round(3))
        with col_d:
            st.markdown("**Theo Độ khó (Difficulty):**")
            st.table(df.groupby("difficulty")[["context_precision", "context_recall", "faithfulness", "answer_relevancy"]].mean().round(3))
            
    with tab3:
        if report_file.exists():
            st.markdown(report_file.read_text(encoding="utf-8"))