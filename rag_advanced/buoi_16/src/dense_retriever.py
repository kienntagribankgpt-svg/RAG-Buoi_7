import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class DenseRetriever:
    def __init__(self, df_corpus, model_name="paraphrase-multilingual-MiniLM-L12-v2", cache_dir=None):
        self.df = df_corpus.copy().reset_index(drop=True)
        self.model = SentenceTransformer(model_name)
        self.cache_file = Path(cache_dir) / "dense_embeddings.pkl" if cache_dir else None
        self.embeddings = self._get_or_compute_embeddings()
        
    def _get_or_compute_embeddings(self):
        if self.cache_file and self.cache_file.exists():
            with open(self.cache_file, "rb") as f:
                return pickle.load(f)
        emb = self.model.encode(self.df["text"].tolist(), show_progress_bar=False, normalize_embeddings=True)
        if self.cache_file:
            with open(self.cache_file, "wb") as f:
                pickle.dump(emb, f)
        return emb
        
    def retrieve(self, query, top_k=5):
        query_emb = self.model.encode([query], normalize_embeddings=True)
        sim_scores = cosine_similarity(query_emb, self.embeddings)[0]
        top_indices = np.argsort(sim_scores)[::-1][:top_k]
        
        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = self.df.iloc[idx]
            results.append({
                "rank": rank,
                "chunk_id": row["chunk_id"],
                "document_id": row["document_id"],
                "text": row["text"],
                "retrieval_score": float(sim_scores[idx]),
                "retrieval_method": "Dense",
                "citation": row["citation"]
            })
        return results