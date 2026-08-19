import re
import pandas as pd
from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, df_corpus):
        self.df = df_corpus.copy().reset_index(drop=True)
        self.tokenized_corpus = [self._tokenize(t) for t in self.df["text"]]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        
    def _tokenize(self, text):
        if not isinstance(text, str):
            return []
        tokens = re.findall(r"\w+|[^\w\s]", text.lower(), re.UNICODE)
        return [t for t in tokens if len(t.strip()) > 0]
        
    def retrieve(self, query, top_k=5):
        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = self.df.iloc[idx]
            results.append({
                "rank": rank,
                "chunk_id": row["chunk_id"],
                "document_id": row["document_id"],
                "text": row["text"],
                "retrieval_score": float(scores[idx]),
                "retrieval_method": "BM25",
                "citation": row["citation"]
            })
        return results