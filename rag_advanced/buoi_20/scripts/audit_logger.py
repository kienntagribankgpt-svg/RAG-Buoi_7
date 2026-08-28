import os, json, uuid
from datetime import datetime, timezone
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
log_file = base_dir / "outputs" / "audit_log.jsonl"
log_file.parent.mkdir(parents=True, exist_ok=True)

def log_audit_event(user_id_demo: str, user_role: str, action: str, query: str, retrieved_docs: list = None, citations: list = None, status: str = "SUCCESS", details: dict = None) -> str:
    req_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "request_id": req_id,
        "user_id_demo": user_id_demo,
        "user_role": user_role,
        "action": action,
        "query": query,
        "retrieved_docs": retrieved_docs or [],
        "citations": citations or [],
        "status": status,
        "details": details or {}
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return req_id
