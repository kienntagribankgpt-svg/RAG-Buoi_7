import sys
import argparse
import pandas as pd
from pathlib import Path

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_15")
sys.path.append(str(base_dir))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever
from src.reranker import Reranker

parser = argparse.ArgumentParser()
parser.add_argument("--query", type=str, default="Điều kiện vay vốn và các nhu cầu vốn không được cho vay?")
parser.add_argument("--method", type=str, default="hybrid_rerank", choices=["bm25", "dense", "hybrid", "hybrid_rerank"])
parser.add_argument("--top-k", type=int, default=3)
args = parser.parse_args()

df_corpus = pd.read_csv(base_dir / "data" / "processed" / "chunks_normalized.csv")
bm25 = BM25Retriever(df_corpus)
dense = DenseRetriever(df_corpus, cache_dir=base_dir / "cache")
hybrid = HybridRetriever(bm25, dense)
reranker = Reranker()

if args.method == "bm25":
    results = bm25.retrieve(args.query, top_k=args.top_k)
elif args.method == "dense":
    results = dense.retrieve(args.query, top_k=args.top_k)
elif args.method == "hybrid":
    results = hybrid.retrieve(args.query, top_k=args.top_k)
else:
    cands = hybrid.retrieve(args.query, top_k=15, candidate_k=15)
    results = reranker.rerank(args.query, cands, top_k=args.top_k)

print("=" * 70)
print(f"QUERY: '{args.query}' | METHOD: {args.method.upper()}")
print("=" * 70)

retrieved_docs = set()
for r in results:
    rank = r.get("final_rank", r.get("rank"))
    score = r.get("rerank_score", r.get("rrf_score", r.get("retrieval_score", 0.0)))
    retrieved_docs.add(r["document_id"])
    print(f"\n[Rank {rank}] Chunk ID: {r['chunk_id']} (Document: {r['document_id']}) - Score: {score:.4f}")
    print(f"Citation: {r['citation']}")
    print(f"Text: {r['text'][:120]}...")

print("\n" + "=" * 70)
print("GRAPH HINTS (MỐI QUAN HỆ CẤU TRÚC PHÁP LÝ):")
print(f"- Các văn bản liên quan trực tiếp: {list(retrieved_docs)}")
print("- Quan hệ đồ thị có thể khám phá tiếp trên Neo4j: (:VanBan)-[:CONTAINS]->(:DieuKhoan)")
print("=" * 70)
