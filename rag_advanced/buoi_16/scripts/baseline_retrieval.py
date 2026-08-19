import sys
import argparse
import pandas as pd
from pathlib import Path

# Thêm thư mục gốc vào sys.path
base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_14")
sys.path.append(str(base_dir))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever

parser = argparse.ArgumentParser()
parser.add_argument("--query", type=str, default="Quy định về hạn mức và điều kiện cho vay?")
parser.add_argument("--top-k", type=int, default=3)
args = parser.parse_args()

corpus_path = base_dir / "data" / "processed" / "chunks_normalized.csv"
df_corpus = pd.read_csv(corpus_path)

bm25 = BM25Retriever(df_corpus)
dense = DenseRetriever(df_corpus, cache_dir=base_dir / "cache")

print("=" * 70)
print(f"QUERY: '{args.query}'")
print("=" * 70)

print("\n--- BM25 RESULTS ---")
for res in bm25.retrieve(args.query, top_k=args.top_k):
    print(f"Rank {res['rank']} (Score: {res['retrieval_score']:.4f}) | {res['chunk_id']}")
    print(f"Citation: {res['citation']}")
    print(f"Text: {res['text'][:90]}...\n")

print("--- DENSE RESULTS ---")
for res in dense.retrieve(args.query, top_k=args.top_k):
    print(f"Rank {res['rank']} (Score: {res['retrieval_score']:.4f}) | {res['chunk_id']}")
    print(f"Citation: {res['citation']}")
    print(f"Text: {res['text'][:90]}...\n")