import json
import pandas as pd
from pathlib import Path
from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever
from src.reranker import Reranker

class SecureRetriever:
    def __init__(self, corpus_path, cache_dir):
        self.df_all = pd.read_csv(corpus_path)
        self.cache_dir = cache_dir
        
        def parse_roles(x):
            if isinstance(x, list): return x
            try: return json.loads(str(x).replace("'", '"'))
            except: return [str(x)]
            
        self.df_all["allowed_roles_list"] = self.df_all["allowed_roles"].apply(parse_roles)
        
        # Khởi tạo sẵn các bộ tìm kiếm nền tảng trên toàn bộ dữ liệu (đã có cache embeddings)
        self.bm25_full = BM25Retriever(self.df_all)
        self.dense_full = DenseRetriever(self.df_all, cache_dir=self.cache_dir)
        self.hybrid_full = HybridRetriever(self.bm25_full, self.dense_full)
        self.reranker = Reranker()
        
    def _is_accessible(self, chunk_roles, user_roles):
        if not user_roles:
            return False
        return any(role in chunk_roles for role in user_roles)

    def retrieve(self, query, user_roles, method="hybrid_rerank", top_k=5, candidate_k=25):
        if not user_roles:
            return [], len(self.df_all)
            
        # Tập hợp các chunk_id hợp lệ với vai trò hiện tại
        mask = self.df_all["allowed_roles_list"].apply(lambda r: self._is_accessible(r, user_roles))
        allowed_chunk_ids = set(self.df_all[mask]["chunk_id"].tolist())
        total_filtered_out = len(self.df_all) - len(allowed_chunk_ids)
        
        if not allowed_chunk_ids:
            return [], total_filtered_out
            
        # Lấy ứng viên rộng từ hệ thống tìm kiếm
        raw_candidates = []
        if method == "bm25":
            raw_candidates = self.bm25_full.retrieve(query, top_k=candidate_k)
        elif method == "dense":
            raw_candidates = self.dense_full.retrieve(query, top_k=candidate_k)
        else: # hybrid & hybrid_rerank
            raw_candidates = self.hybrid_full.retrieve(query, top_k=candidate_k, candidate_k=candidate_k)
            
        # Lọc bảo mật: Chỉ giữ lại các chunk mà người dùng có quyền truy cập
        secure_candidates = [c for c in raw_candidates if c["chunk_id"] in allowed_chunk_ids]
        
        # Bổ sung thông tin allowed_roles vào kết quả
        role_map = dict(zip(self.df_all["chunk_id"], self.df_all["allowed_roles_list"]))
        for c in secure_candidates:
            c["allowed_roles"] = role_map.get(c["chunk_id"], [])
            
        if method == "hybrid_rerank" and secure_candidates:
            final_results = self.reranker.rerank(query, secure_candidates, top_k=top_k)
        else:
            final_results = secure_candidates[:top_k]
            for idx, r in enumerate(final_results, 1):
                r["final_rank"] = idx
                
        return final_results, total_filtered_out
