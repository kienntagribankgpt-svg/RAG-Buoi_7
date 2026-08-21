import os
import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple

base_dir = Path(r"D:/du_an_cua_ban/RAG/rag_advanced/buoi_17")

# 1. Ghi đè scripts/secure_retrieval.py chuẩn hóa RBAC
secure_code = """import os
import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple

base_dir = Path(r"D:/du_an_cua_ban/RAG/rag_advanced/buoi_17")

class SecureRetrievalAdapter:
    def __init__(self):
        csv_path = base_dir / "data" / "chunks_combined_secure.csv"
        if not csv_path.exists():
            csv_path = base_dir / "data" / "agribank_internal_policies.csv"
        self.chunks_df = pd.read_csv(csv_path)

    def retrieve_with_rbac(
        self,
        query: str,
        user_role: str,
        method: str = "hybrid_rerank",
        top_k: int = 3
    ) -> Tuple[List[Dict], int, str]:
        # 1. Guest hoặc Unknown role: Default Deny
        if user_role in ["Guest", "Unknown", None, ""]:
            return [], len(self.chunks_df), "DENIED"

        # 2. RBAC Filtering
        allowed_rows = []
        denied_count = 0
        
        for _, row in self.chunks_df.iterrows():
            roles_val = str(row.get("allowed_roles", "Common")).upper()
            
            # Admin & KiemToanVien có toàn quyền tra cứu
            if user_role in ["Admin", "KiemToanVien"]:
                allowed_rows.append(row)
            else:
                # Kiểm tra quyền chi tiết theo từng role
                role_upper = user_role.upper()
                if (role_upper in roles_val) or ("COMMON" in roles_val) or ("PUBLIC" in roles_val) or ("ALL" in roles_val) or (roles_val in ["NAN", ""]):
                    allowed_rows.append(row)
                else:
                    denied_count += 1
                
        if not allowed_rows:
            return [], denied_count, "DENIED"

        filtered_df = pd.DataFrame(allowed_rows)
        query_words = [w.lower() for w in query.replace("?", "").replace(",", "").replace("/", " ").replace("-", " ").split() if len(w) > 1]
        
        def calc_score(row):
            txt = " ".join([str(val) for val in row.values]).lower()
            return sum(txt.count(w) for w in query_words)

        filtered_df["score"] = filtered_df.apply(calc_score, axis=1)
        scored_df = filtered_df.sort_values(by="score", ascending=False)
        top_df = scored_df.head(top_k)

        standardized_docs = []
        for rank, (_, doc) in enumerate(top_df.iterrows(), 1):
            text_val = str(doc.get("text") or doc.get("content") or doc.get("noi_dung") or "")
            if len(text_val) < 20:
                text_val = " ".join([str(v) for k, v in doc.items() if k not in ["chunk_id", "document_id", "allowed_roles"]])
            doc_id = str(doc.get("document_id") or doc.get("so_ky_hieu") or "DOC_REF")
            citation = str(doc.get("citation") or doc.get("title") or f"Văn bản {doc_id}")
            standardized_docs.append({
                "rank": rank,
                "chunk_id": str(doc.get("chunk_id", f"chk_{rank}")),
                "document_id": doc_id,
                "title": str(doc.get("title", citation)),
                "citation": citation,
                "text": text_val,
                "allowed_roles": str(doc.get("allowed_roles", "Common")),
                "access_decision": "ALLOWED"
            })
        return standardized_docs, denied_count, "SUCCESS"
"""
(base_dir / "scripts" / "secure_retrieval.py").write_text(secure_code, encoding="utf-8")

# 2. Ghi đè scripts/internal_lookup.py
lookup_code = """import sys
from pathlib import Path

base_dir = Path(r"D:/du_an_cua_ban/RAG/rag_advanced/buoi_17")
sys.path.append(str(base_dir))

from scripts.secure_retrieval import SecureRetrievalAdapter
from scripts.audit_logger import log_audit_event

adapter = SecureRetrievalAdapter()

def internal_lookup(question: str, user_role: str, user_id_demo: str = "demo_user", top_k: int = 3) -> dict:
    docs, denied_count, status = adapter.retrieve_with_rbac(query=question, user_role=user_role, top_k=top_k)
    doc_ids = [d["document_id"] for d in docs]
    chunk_ids = [d["chunk_id"] for d in docs]
    citations = [d["citation"] for d in docs]
    
    if not docs or status == "DENIED":
        answer = "Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập."
        access_decision = "DENIED / NO ACCESS"
        final_status = "DENIED"
    else:
        main_text = docs[0]["text"][:400]
        answer = f"Căn cứ theo quy định nội bộ:\\n\\n{main_text}...\\n\\n(Trích dẫn nguồn: {docs[0]['citation']})"
        access_decision = "ALLOWED"
        final_status = "SUCCESS"

    req_id = log_audit_event(
        user_id_demo=user_id_demo,
        user_role=user_role,
        action="INTERNAL_LOOKUP",
        query=question,
        retrieved_doc_ids=doc_ids,
        retrieved_chunk_ids=chunk_ids,
        citation_ids=citations,
        denied_candidates_count=denied_count,
        status=final_status
    )
    return {
        "request_id": req_id,
        "question": question,
        "user_role": user_role,
        "answer": answer,
        "citations": citations,
        "retrieved_docs": docs,
        "access_decision": access_decision,
        "denied_count": denied_count
    }
"""
(base_dir / "scripts" / "internal_lookup.py").write_text(lookup_code, encoding="utf-8")
print("✔ ĐÃ CẬP NHẬT XONG BỘ LỌC RBAC!")