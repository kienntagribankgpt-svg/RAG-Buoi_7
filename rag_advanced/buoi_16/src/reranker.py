from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.is_fallback = False
        try:
            print(f"[*] Đang nạp mô hình Reranker: {model_name}...")
            self.model = CrossEncoder(model_name)
        except Exception as e:
            print(f"⚠ Không thể tải CrossEncoder ({e}), chuyển sang chế độ FALLBACK.")
            self.is_fallback = True
            
    def rerank(self, query, candidates, top_k=5):
        if not candidates:
            return []
        
        if self.is_fallback:
            for rank, c in enumerate(candidates[:top_k], 1):
                c["final_rank"] = rank
                c["rerank_score"] = c.get("rrf_score", 0.0)
                c["retrieval_method"] = "Hybrid + Rerank (FALLBACK)"
            return candidates[:top_k]
            
        pairs = [[query, c["text"]] for c in candidates]
        scores = self.model.predict(pairs)
        
        for c, s in zip(candidates, scores):
            c["rerank_score"] = float(s)
            
        sorted_candidates = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_k]
        
        results = []
        for rank, c in enumerate(sorted_candidates, 1):
            c_copy = dict(c)
            c_copy["final_rank"] = rank
            c_copy["retrieval_method"] = "Hybrid + Rerank (Cross-Encoder)"
            results.append(c_copy)
            
        return results