import pandas as pd
from collections import defaultdict

class HybridRetriever:
    def __init__(self, bm25_retriever, dense_retriever, rrf_k=60):
        self.bm25_retriever = bm25_retriever
        self.dense_retriever = dense_retriever
        self.rrf_k = rrf_k
        self.df_corpus = bm25_retriever.df

    def retrieve(self, query, top_k=5, candidate_k=20):
        bm25_results = self.bm25_retriever.retrieve(query, top_k=candidate_k)
        dense_results = self.dense_retriever.retrieve(query, top_k=candidate_k)
        
        bm25_ranks = {r["chunk_id"]: r["rank"] for r in bm25_results}
        dense_ranks = {r["chunk_id"]: r["rank"] for r in dense_results}
        
        all_chunk_ids = set(bm25_ranks.keys()) | set(dense_ranks.keys())
        
        rrf_scores = {}
        for c_id in all_chunk_ids:
            score = 0.0
            if c_id in bm25_ranks:
                score += 1.0 / (self.rrf_k + bm25_ranks[c_id])
            if c_id in dense_ranks:
                score += 1.0 / (self.rrf_k + dense_ranks[c_id])
            rrf_scores[c_id] = score
            
        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        chunk_map = {row["chunk_id"]: row for _, row in self.df_corpus.iterrows()}
        
        for rank, (c_id, score) in enumerate(sorted_chunks, 1):
            row = chunk_map.get(c_id)
            results.append({
                "final_rank": rank,
                "chunk_id": c_id,
                "document_id": row["document_id"],
                "bm25_rank": bm25_ranks.get(c_id, "-"),
                "dense_rank": dense_ranks.get(c_id, "-"),
                "rrf_score": score,
                "retrieval_method": "Hybrid (RRF)",
                "text": row["text"],
                "citation": row["citation"]
            })
        return results
