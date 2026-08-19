# 📊 BUỔI 16: ĐÁNH GIÁ HIỆU NĂNG HỆ THỐNG RAG (RAG EVALUATION) BẰNG RAGAS

## 📌 Tổng quan kiến trúc đánh giá
Hệ thống sử dụng phương pháp **LLM-as-a-Judge** với 2 mô hình độc lập qua Hugging Face Router API:
- **Model Pipeline (Generator):** Qwen/Qwen3.5-9B:deepinfra
- **Model Judger (Evaluator):** openai/gpt-oss-20b:deepinfra

---

## 📈 Kết quả 4 Metrics Ragas

| Chỉ số Metric | Điểm đạt được | Ngưỡng mục tiêu | Trạng thái |
| :--- | :---: | :---: | :---: |
| **Context Precision** (Độ chuẩn xác ngữ cảnh) | **0.9280** | >= 0.80 | ✅ ĐẠT |
| **Context Recall** (Độ bao phủ ngữ cảnh) | **0.8200** | >= 0.75 | ✅ ĐẠT |
| **Faithfulness** (Độ trung thực / Không ảo tưởng) | **0.9640** | >= 0.85 | ✅ ĐẠT |
| **Answer Relevancy** (Độ phù hợp câu trả lời) | **0.8560** | >= 0.80 | ✅ ĐẠT |
| **⭐ ĐIỂM TỔNG HỢP RAGAS SCORE** | **0.8920** | >= 0.80 | **EXCELLENT** |

---

## 📁 Cấu trúc dữ liệu & Báo cáo
- **Golden Dataset (20 Q&A):** data/eval/qa_dataset.csv
- **Chi tiết chấm điểm từng câu hỏi:** data/eval/evaluation_results.csv
- **Báo cáo phân tích chuyên sâu & giải pháp:** outputs/ragas_evaluation_report.md

---

## 🚀 Hướng dẫn chạy lại quy trình đánh giá
python scripts/evaluate_rag_pipeline.py
