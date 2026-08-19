import sys
import argparse
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_14")
sys.path.append(str(base_dir))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever
from src.reranker import Reranker

parser = argparse.ArgumentParser()
parser.add_argument("--query", type=str, default="Quy định về thẩm quyền phê duyệt và hạn mức cho vay?")
parser.add_argument("--candidate-k", type=int, default=15)
parser.add_argument("--top-k", type=int, default=5)
args = parser.parse_args()

corpus_path = base_dir / "data" / "processed" / "chunks_normalized.csv"
df_corpus = pd.read_csv(corpus_path)

bm25 = BM25Retriever(df_corpus)
dense = DenseRetriever(df_corpus, cache_dir=base_dir / "cache")
hybrid = HybridRetriever(bm25, dense)
reranker = Reranker()

print("=" * 75)
print(f"QUERY: '{args.query}'")
print("=" * 75)

# Lấy Candidates từ Hybrid
candidates = hybrid.retrieve(args.query, top_k=args.candidate_k, candidate_k=args.candidate_k)

print("\n--- 1. BEFORE RERANK (HYBRID RRF TOP-5) ---")
for r in candidates[:args.top_k]:
    print(f"Top {r['final_rank']} | Chunk: {r['chunk_id']} | BM25 Rank: {r['bm25_rank']} | Dense Rank: {r['dense_rank']} | RRF Score: {r['rrf_score']:.5f}")
    print(f"Citation: {r['citation']}")
    print(f"Text: {r['text'][:85]}...\n")

# Chạy Reranker
final_results = reranker.rerank(args.query, candidates, top_k=args.top_k)

print("--- 2. AFTER RERANK (CROSS-ENCODER TOP-5) ---")
for r in final_results:
    print(f"Top {r['final_rank']} | Chunk: {r['chunk_id']} | Rerank Score: {r['rerank_score']:.4f}")
    print(f"Citation: {r['citation']}")
    print(f"Text: {r['text'][:85]}...\n")