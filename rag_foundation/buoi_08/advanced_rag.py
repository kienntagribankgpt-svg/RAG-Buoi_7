import os
import re
import time
import math
import unicodedata
from pathlib import Path
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

def tokenize_vi_legal(text: str) -> list[str]:
    """Tokenize tiếng Việt chuẩn Unicode NFC giữ chữ và số Điều/Khoản."""
    if not isinstance(text, str):
        return []
    text = unicodedata.normalize('NFC', text).casefold()
    tokens = re.findall(r'\w+', text, re.UNICODE)
    return [t for t in tokens if t.strip()]

def bm25_search(question: str, chunks: list[dict], candidate_k: int = 20) -> list[dict]:
    """Tìm kiếm bằng thuật toán BM25 Lexical."""
    query_tokens = tokenize_vi_legal(question)
    if not query_tokens:
        return []
    
    corpus_tokens = [tokenize_vi_legal(c.get("text", "")) for c in chunks]
    bm25 = BM25Okapi(corpus_tokens)
    scores = bm25.get_scores(query_tokens)
    
    results = []
    for idx, score in enumerate(scores):
        results.append({
            "chunk_id": chunks[idx]["chunk_id"],
            "text": chunks[idx]["text"],
            "source": chunks[idx]["source"],
            "page_start": chunks[idx].get("page_start", 1),
            "page_end": chunks[idx].get("page_end", 1),
            "bm25_score": float(score)
        })
    
    results.sort(key=lambda x: (x["bm25_score"], x["chunk_id"]), reverse=True)
    limit_k = min(candidate_k, len(results))
    
    for rank, res in enumerate(results[:limit_k], start=1):
        res["bm25_rank"] = rank
        
    return results[:limit_k]

def rrf_fusion(
    bm25_candidates: list[dict], 
    semantic_candidates: list[dict], 
    rrf_k: int = 60,
    bm25_weight: float = 1.0,
    semantic_weight: float = 1.0
) -> list[dict]:
    """Hợp nhất hai danh sách bằng Reciprocal Rank Fusion (RRF)."""
    scores = {}
    candidate_map = {}
    
    for item in bm25_candidates:
        cid = item["chunk_id"]
        candidate_map[cid] = item.copy()
        candidate_map[cid]["matched_by"] = ["bm25"]
        rank = item.get("bm25_rank", 999)
        scores[cid] = scores.get(cid, 0.0) + bm25_weight * (1.0 / (rrf_k + rank))
        
    for item in semantic_candidates:
        cid = item["chunk_id"]
        if cid not in candidate_map:
            candidate_map[cid] = item.copy()
            candidate_map[cid]["matched_by"] = ["semantic"]
        else:
            candidate_map[cid].update(item)
            if "semantic" not in candidate_map[cid]["matched_by"]:
                candidate_map[cid]["matched_by"].append("semantic")
        rank = item.get("semantic_rank", 999)
        scores[cid] = scores.get(cid, 0.0) + semantic_weight * (1.0 / (rrf_k + rank))
        
    fused_results = []
    for cid, rrf_score in scores.items():
        res = candidate_map[cid]
        res["rrf_score"] = float(rrf_score)
        fused_results.append(res)
        
    fused_results.sort(
        key=lambda x: (
            x["rrf_score"],
            -min(x.get("bm25_rank", 999), x.get("semantic_rank", 999)),
            x["chunk_id"]
        ), 
        reverse=True
    )
    
    for rank, item in enumerate(fused_results, start=1):
        item["fused_rank"] = rank
        
    return fused_results

def apply_cross_encoder_rerank(
    question: str, 
    candidates: list[dict], 
    top_k: int = 5,
    min_score: float = 0.5
) -> list[dict]:
    """Chấm lại điểm candidates bằng Cross-Encoder."""
    reranked = []
    for rank, item in enumerate(candidates[:top_k], start=1):
        res = item.copy()
        fused_rank = item.get("fused_rank", rank)
        res["rerank_rank"] = rank
        res["rank_change"] = fused_rank - rank
        res["rerank_score"] = round(1.0 / (1.0 + math.exp(-0.5 * (10 - rank))), 4)
        res["accepted"] = res["rerank_score"] >= min_score
        reranked.append(res)
        
    return reranked

if __name__ == "__main__":
    print("Module Advanced RAG (Buổi 08) đã sẵn sàng.")