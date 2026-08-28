import os, sys, pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from scripts.audit_logger import log_audit_event

def run_uc1_lookup(query: str, role: str, user_id: str):
    if role == "Guest":
        req_id = log_audit_event(user_id, role, "UC1_LOOKUP", query, status="DENIED", details={"reason": "RBAC Denied"})
        return {"access": "DENIED", "request_id": req_id, "answer": "Truy cập bị từ chối theo chính sách RBAC.", "docs": []}
    docs = [
        {"rank": 1, "citation": "Điều 6 Thông tư 52/VBHN-NHNN", "doc_id": "DOC-52-NHNN-06", "text": "Hồ sơ đề nghị cấp Giấy phép thành lập Văn phòng đại diện lập thành 01 bộ bản gốc.", "allowed": ["Admin", "KiemToanVien", "HR"]},
        {"rank": 2, "citation": "Điều 12 Quyết định 215/QĐ-NHNO-RR", "doc_id": "DOC-215-RR-12", "text": "Tỷ lệ an toàn vốn tối thiểu (CAR) mục tiêu nội bộ không thấp hơn 9.0%.", "allowed": ["Admin", "KiemToanVien", "Risk_Manager"]}
    ]
    req_id = log_audit_event(user_id, role, "UC1_LOOKUP", query, [d["doc_id"] for d in docs], [d["citation"] for d in docs], status="ALLOWED")
    return {"access": "ALLOWED", "request_id": req_id, "answer": f"Căn cứ Điều 6 Thông tư 52/VBHN-NHNN và Điều 12 QĐ 215/QĐ-NHNO-RR, hồ sơ và tỷ lệ an toàn áp dụng đúng thẩm quyền {role}.", "docs": docs}

def run_uc2_gap_checker(role: str, user_id: str):
    if role == "Guest": return pd.DataFrame()
    data = [
        {"gap_id": "GAP_01", "external_doc": "Thông tư 01/2014/TT-NHNN", "classification": "DAP_UNG", "confidence": 0.95, "review_status": "NEEDS_HUMAN_REVIEW"},
        {"gap_id": "GAP_02", "external_doc": "Thông tư 41/2016/TT-NHNN", "classification": "CHENH_LECH", "confidence": 0.90, "review_status": "NEEDS_HUMAN_REVIEW"},
        {"gap_id": "GAP_03", "external_doc": "Thông tư 13/2018/TT-NHNN", "classification": "CHUA_DU_BANG_CHUNG", "confidence": 0.70, "review_status": "NEEDS_HUMAN_REVIEW"}
    ]
    for d in data:
        d["request_id"] = log_audit_event(user_id, role, "UC2_GAP_CHECK", d["external_doc"], status="SUCCESS")
    return pd.DataFrame(data)

def run_uc3_conflict_checker(role: str, user_id: str):
    if role == "Guest": return pd.DataFrame()
    data = [
        {"conflict_id": "CFL_01", "domain": "An toàn kho quỹ", "doc_a": "Điều 8 QĐ 100/QĐ-NHNO-AT (Xe bán tải)", "doc_b": "Điều 5 TT 01/2014/TT-NHNN (Xe bọc thép chuyên dùng)", "severity": "HIGH", "review_status": "NEEDS_HUMAN_REVIEW"},
        {"conflict_id": "CFL_02", "domain": "Quản lý CAR", "doc_a": "Điều 12 QĐ 215/QĐ-NHNO-RR (CAR >= 9.0%)", "doc_b": "Điều 9 TT 41/2016/TT-NHNN (CAR >= 8.0%)", "severity": "LOW", "review_status": "NEEDS_HUMAN_REVIEW"},
        {"conflict_id": "CFL_03", "domain": "Phân quyền tín dụng", "doc_a": "Điều 4 QĐ 350/QĐ-NHNO-TD (Duyệt cá nhân 20 tỷ)", "doc_b": "Điều 2 NQ 18/NQ-HĐTV (Họp Hội đồng > 15 tỷ)", "severity": "HIGH", "review_status": "NEEDS_HUMAN_REVIEW"}
    ]
    for d in data:
        d["request_id"] = log_audit_event(user_id, role, "UC3_CONFLICT_CHECK", d["domain"], status="SUCCESS")
    return pd.DataFrame(data)

def run_uc4_checklist_gen(domain: str, unit: str, role: str, user_id: str):
    if role == "Guest": return pd.DataFrame()
    data = [
        {"item_id": "CHK_KHO_01", "domain": "Kho quỹ & Vận chuyển", "unit": unit, "question": "Chi nhánh có sử dụng xe bọc thép chuyên dùng và 2 vệ sĩ áp tải?", "risk_level": "HIGH", "citation": "Điều 5 TT 01/2014/TT-NHNN & Điều 8 QĐ 100/QĐ-NHNO-AT", "review_status": "NEEDS_HUMAN_REVIEW"},
        {"item_id": "CHK_CNTT_01", "domain": "Bảo mật CNTT & AI", "unit": unit, "question": "Hệ thống RAG và vector DB có mã hóa At-Rest AES-128 và lưu audit logs?", "risk_level": "HIGH", "citation": "Điều 9 & 16 Quy chế 600/QĐ-NHNO-CNTT", "review_status": "NEEDS_HUMAN_REVIEW"},
        {"item_id": "CHK_TD_01", "domain": "Phân quyền tín dụng", "unit": unit, "question": "Khoản vay trên 15 tỷ đồng có biên bản họp Hội đồng Tín dụng Chi nhánh?", "risk_level": "HIGH", "citation": "Điều 2 NQ 18/NQ-HĐTV & Điều 4 QĐ 350/QĐ-NHNO-TD", "review_status": "NEEDS_HUMAN_REVIEW"}
    ]
    for d in data:
        d["request_id"] = log_audit_event(user_id, role, "UC4_CHECKLIST_GEN", f"{domain} @ {unit}", status="SUCCESS")
    return pd.DataFrame(data)
