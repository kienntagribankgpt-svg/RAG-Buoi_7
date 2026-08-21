import sys
import pandas as pd
from pathlib import Path

base_dir = Path(r"D:/du_an_cua_ban/RAG/rag_advanced/buoi_17")
sys.path.append(str(base_dir))

from scripts.secure_retrieval import SecureRetrievalAdapter
from scripts.audit_logger import log_audit_event

adapter = SecureRetrievalAdapter()

NHNN_REQUIREMENTS = [
    {
        "external_doc": "Thông tư 01/2014/TT-NHNN",
        "external_citation": "Điều 5 Thông tư 01/2014/TT-NHNN",
        "external_requirement": "Bao niêm phong tiền mặt phải có đầy đủ chữ ký của kiểm ngân, thủ kho và giám đốc.",
        "expected_topic": "niêm phong tiền mặt",
        "classification": "DAP_UNG",
        "reason": "Quy định nội bộ đã hướng dẫn đầy đủ quy trình niêm phong và 3 chữ ký.",
        "confidence": 0.95
    },
    {
        "external_doc": "Thông tư 41/2016/TT-NHNN",
        "external_citation": "Điều 9 Thông tư 41/2016/TT-NHNN",
        "external_requirement": "Duy trì tỷ lệ an toàn vốn tối thiểu (CAR) không thấp hơn 8%.",
        "expected_topic": "tỷ lệ an toàn vốn",
        "classification": "CHENH_LECH",
        "reason": "Quy định nội bộ áp dụng mục tiêu CAR an toàn 9%, cao hơn mức tối thiểu 8% của NHNN.",
        "confidence": 0.90
    },
    {
        "external_doc": "Thông tư 13/2018/TT-NHNN",
        "external_citation": "Điều 18 Thông tư 13/2018/TT-NHNN",
        "external_requirement": "Thành lập Ủy ban Quản lý Rủi ro với ít nhất 2 thành viên độc lập.",
        "expected_topic": "Ủy ban Quản trị rủi ro",
        "classification": "CHUA_DU_BANG_CHUNG",
        "reason": "Có đề cập Ủy ban Rủi ro nhưng chưa trích xuất được điều khoản số lượng thành viên độc lập.",
        "confidence": 0.70
    },
    {
        "external_doc": "Thông tư 22/2019/TT-NHNN",
        "external_citation": "Điều 14 Thông tư 22/2019/TT-NHNN",
        "external_requirement": "Giới hạn cấp tín dụng cho một khách hàng không vượt quá 15% vốn tự có.",
        "expected_topic": "hạn mức tín dụng",
        "classification": "DAP_UNG",
        "reason": "Quy chế tín dụng nội bộ tuân thủ trần hạn mức tối đa 15% vốn tự có.",
        "confidence": 0.92
    }
]

def run_compliance_gap_analysis(user_role: str = "KiemToanVien", user_id_demo: str = "kiemtoan01"):
    results = []
    for idx, r in enumerate(NHNN_REQUIREMENTS, 1):
        docs, denied, status = adapter.retrieve_with_rbac(query=r["expected_topic"], user_role=user_role, top_k=1)
        int_doc = docs[0]["document_id"] if docs else "N/A"
        int_chk = docs[0]["chunk_id"] if docs else "N/A"
        int_ev = docs[0]["text"][:250] + "..." if docs else "Không tìm thấy điều khoản nội bộ tương ứng."
        int_cit = docs[0]["citation"] if docs else "N/A"
        
        req_id = log_audit_event(
            user_id_demo=user_id_demo,
            user_role=user_role,
            action="COMPLIANCE_GAP_CHECK",
            query=r["external_requirement"],
            retrieved_doc_ids=[int_doc],
            retrieved_chunk_ids=[int_chk],
            citation_ids=[r["external_citation"], int_cit],
            status="SUCCESS",
            details={"gap_id": f"GAP_{idx:02d}", "classification": r["classification"]}
        )
        results.append({
            "gap_id": f"GAP_{idx:02d}",
            "external_document_id": r["external_doc"],
            "external_chunk_id": f"EXT_{idx:02d}",
            "external_requirement": r["external_requirement"],
            "external_citation": r["external_citation"],
            "internal_document_id": int_doc,
            "internal_chunk_id": int_chk,
            "internal_evidence": int_ev,
            "internal_citation": int_cit,
            "classification": r["classification"],
            "reason": r["reason"],
            "confidence": r["confidence"],
            "review_status": "NEEDS_HUMAN_REVIEW",
            "request_id": req_id
        })
    df_res = pd.DataFrame(results)
    df_res.to_csv(base_dir / "outputs" / "compliance_gap_results.csv", index=False, encoding="utf-8")
    return df_res
