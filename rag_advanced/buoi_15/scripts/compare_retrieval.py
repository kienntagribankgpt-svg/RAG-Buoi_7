import sys
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_15")
sys.path.append(str(base_dir))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever
from src.reranker import Reranker

print("=" * 70)
print("PROMPT 5: BENCHMARK RETRIEVAL METRICS (HIT@K)")
print("=" * 70)

df_corpus = pd.read_csv(base_dir / "data" / "processed" / "chunks_normalized.csv")
df_questions = pd.read_csv(base_dir / "data" / "eval" / "questions.csv")

bm25 = BM25Retriever(df_corpus)
dense = DenseRetriever(df_corpus, cache_dir=base_dir / "cache")
hybrid = HybridRetriever(bm25, dense)
reranker = Reranker()

methods = ["BM25", "Dense", "Hybrid", "Hybrid + Rerank"]
results_comparison = []

hit1 = {m: 0 for m in methods}
hit3 = {m: 0 for m in methods}
hit5 = {m: 0 for m in methods}

for _, q_row in df_questions.iterrows():
    qid = q_row["question_id"]
    query = q_row["question"]
    exp_chunk = str(q_row["expected_chunk_id"]).strip()
    
    # 1. BM25
    r_bm25 = [r["chunk_id"] for r in bm25.retrieve(query, top_k=5)]
    # 2. Dense
    r_dense = [r["chunk_id"] for r in dense.retrieve(query, top_k=5)]
    # 3. Hybrid
    hyb_cands = hybrid.retrieve(query, top_k=15, candidate_k=15)
    r_hyb = [r["chunk_id"] for r in hyb_cands[:5]]
    # 4. Rerank
    r_rerank = [r["chunk_id"] for r in reranker.rerank(query, hyb_cands, top_k=5)]
    
    all_runs = {"BM25": r_bm25, "Dense": r_dense, "Hybrid": r_hyb, "Hybrid + Rerank": r_rerank}
    
    for m, ranks in all_runs.items():
        h1 = 1 if exp_chunk in ranks[:1] else 0
        h3 = 1 if exp_chunk in ranks[:3] else 0
        h5 = 1 if exp_chunk in ranks[:5] else 0
        
        hit1[m] += h1
        hit3[m] += h3
        hit5[m] += h5
        
        rank_pos = (ranks.index(exp_chunk) + 1) if exp_chunk in ranks else -1
        results_comparison.append({
            "question_id": qid,
            "query_type": q_row["query_type"],
            "method": m,
            "expected_chunk": exp_chunk,
            "found_rank": rank_pos,
            "hit@1": h1,
            "hit@3": h3,
            "hit@5": h5
        })

df_res = pd.DataFrame(results_comparison)
df_res.to_csv(base_dir / "outputs" / "retrieval_comparison.csv", index=False, encoding="utf-8")

total_q = len(df_questions)
print(f"Tổng số câu hỏi đánh giá: {total_q}\n")
report_md = ["# 📊 BÁO CÁO ĐÁNH GIÁ HIỆU NĂNG RETRIEVAL (BUỔI 14)\n", "| Phương pháp | Hit@1 | Hit@3 | Hit@5 |", "| :--- | :--- | :--- | :--- |"]
for m in methods:
    h1_p = (hit1[m] / total_q) * 100
    h3_p = (hit3[m] / total_q) * 100
    h5_p = (hit5[m] / total_q) * 100
    report_md.append(f"| **{m}** | {h1_p:.1f}% | {h3_p:.1f}% | {h5_p:.1f}% |")
    print(f"[{m:16}] Hit@1: {h1_p:5.1f}% | Hit@3: {h3_p:5.1f}% | Hit@5: {h5_p:5.1f}%")

(base_dir / "outputs" / "evaluation_report.md").write_text("\n".join(report_md), encoding="utf-8")
print(f"\n✔ Đã lưu kết quả tại: outputs/evaluation_report.md & outputs/retrieval_comparison.csv")
