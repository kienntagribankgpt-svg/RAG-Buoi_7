import sys
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
        answer = f"Căn cứ theo quy định nội bộ:\n\n{main_text}...\n\n(Trích dẫn nguồn: {docs[0]['citation']})"
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
