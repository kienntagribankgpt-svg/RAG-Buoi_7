"""Streamlit UI for Buoi 07 RAG workshop.

This app calls the CLI functions implemented in rag.py; it does not
reimplement RAG logic. It uses the Buoi_05 Python interpreter when
available to run rag.py commands so the same environment is used.
"""

import streamlit as st
from pathlib import Path
import subprocess
import sys
import json
import shlex


BASE_DIR = Path(__file__).resolve().parent
PY_VENV_WIN = BASE_DIR / ".." / "buoi_05" / ".venv" / "Scripts" / "python.exe"
PY_VENV_UNIX = BASE_DIR / ".." / "buoi_05" / ".venv" / "bin" / "python"


def get_python_exec():
	# prefer Buoi_05 venv python if it exists, else fallback to current
	pwin = PY_VENV_WIN.resolve()
	punix = PY_VENV_UNIX.resolve()
	if pwin.exists():
		return str(pwin)
	if punix.exists():
		return str(punix)
	return sys.executable


def run_rag_cmd(args):
	py = get_python_exec()
	cmd = [py, str(BASE_DIR / "rag.py")] + args
	try:
		proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
	except Exception as e:
		return {"ok": False, "error": str(e), "stdout": "", "stderr": ""}
	return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode}


st.set_page_config(page_title="Buổi 07 — RAG UI", layout="wide")
st.title("Buổi 07 — RAG Workshop (Giao diện)")


# --- Sidebar: status and controls ------------------------------------
with st.sidebar:
	st.header("Trạng thái hệ thống")
	strategy = st.selectbox("Chọn strategy", ["hierarchical", "semantic", "fixed-size"], index=0)
	top_k = st.slider("Top-k", 1, 10, 5)
	st.markdown("---")
	st.write("Kiểm tra cấu hình và collection cho strategy đã chọn:")
	if st.button("Cập nhật trạng thái"):
		st.session_state._status_refresh = True
	# show last status if present
	status_output = {}


def parse_status_text(text: str) -> dict:
	res = {}
	for line in text.splitlines():
		if ":" in line:
			k, v = line.split(":", 1)
			res[k.strip()] = v.strip()
	return res


def get_status(strategy_choice):
	out = run_rag_cmd(["status", "--strategy", strategy_choice])
	if not out["ok"]:
		# still try to parse stdout
		parsed = parse_status_text(out.get("stdout", ""))
		return {"ok": False, "error": out.get("stderr") or out.get("stdout"), "parsed": parsed}
	parsed = parse_status_text(out.get("stdout", ""))
	return {"ok": True, "parsed": parsed}


status_res = get_status(strategy)
api_flag = status_res.get("parsed", {}).get("API Key", "Thiếu")
st.sidebar.write("API Key:", api_flag)
st.sidebar.write("Embedding model:", status_res.get("parsed", {}).get("Embedding model", "-"))
st.sidebar.write("Embedding dim:", status_res.get("parsed", {}).get("Embedding dim", "-"))
st.sidebar.write("Generation model:", status_res.get("parsed", {}).get("Embedding model", "-"))
st.sidebar.write("Strategy:", strategy)
collection_name = status_res.get("parsed", {}).get("Collection name", "-")
st.sidebar.write("Collection:", collection_name)
st.sidebar.write("Collection exists:", status_res.get("parsed", {}).get("Collection exists", "-"))
st.sidebar.write("Số chunk:", status_res.get("parsed", {}).get("Collection record count", "-"))
st.sidebar.write("RAG_MAX_DISTANCE:", status_res.get("parsed", {}).get("RAG_MAX_DISTANCE", "-"))


# --- Main: Index area -----------------------------------------------
col1, col2 = st.columns([1, 2])
with col1:
	st.subheader("Index dữ liệu")
	reset = st.checkbox("Reset collection trước khi index")
	if st.button("Index dữ liệu"):
		# run validate to get stats
		with st.spinner("Đang kiểm tra chunks..."):
			v = run_rag_cmd(["validate", "--strategy", strategy])
		if not v["ok"] and "No valid chunks found" not in v["stdout"]:
			st.error("Lỗi khi kiểm tra chunks: " + (v.get("stderr") or v.get("stdout")))
		else:
			st.info("Thông tin kiểm tra: \n" + v.get("stdout", ""))
		# run index
		with st.spinner("Đang index — có thể mất thời gian..."):
			args = ["index", "--strategy", strategy]
			if reset:
				args.append("--reset")
			out = run_rag_cmd(args)
		if not out["ok"]:
			st.error("Index thất bại: " + (out.get("stderr") or out.get("stdout") or "unknown error"))
		else:
			st.success("Index hoàn tất")
			st.text(out.get("stdout"))

with col2:
	st.subheader("Gửi câu hỏi")
	question = st.text_area("Nhập câu hỏi (tiếng Việt)")
	if st.button("Gửi câu hỏi"):
		if not question or question.strip() == "":
			st.warning("Vui lòng nhập câu hỏi không trống")
		else:
			# call query
			with st.spinner("Đang truy xuất và tạo câu trả lời..."):
				args = ["query", "--strategy", strategy, "--top-k", str(top_k), "--question", question]
				res = run_rag_cmd(args)
			if not res["ok"]:
				st.error("Lỗi khi truy vấn: " + (res.get("stderr") or res.get("stdout") or "unknown"))
			else:
				# parse JSON result
				try:
					parsed = json.loads(res["stdout"])
				except Exception:
					st.error("Không thể phân tích kết quả từ rag.py")
					parsed = None
				if parsed:
					st.markdown(f"**Status:** {parsed.get('status')}")
					if parsed.get("warnings"):
						st.warning("Cảnh báo: " + "; ".join(parsed.get("warnings")))
					if parsed.get("status") == "insufficient_evidence":
						st.info(parsed.get("answer"))
					else:
						st.markdown("**Answer:**")
						st.write(parsed.get("answer"))
					# citations
					if parsed.get("citations"):
						st.subheader("Citations")
						for c in parsed.get("citations"):
							st.write(c.get("display"))
					# evidence
					st.subheader("Nguồn tham khảo")
					evs = parsed.get("evidence", [])
					if not evs:
						st.write("Chưa có evidence")
					for e in evs:
						header = f"{e.get('source')} – " + (f"tr. {e.get('page_start')}" if e.get('page_start')==e.get('page_end') else f"tr. {e.get('page_start')}-{e.get('page_end')}") + f" – {e.get('chunk_id')}"
						with st.expander(header):
							st.write(f"evidence_id: {e.get('evidence_id')}")
							st.write(f"distance: {round(e.get('distance',0), 4)}")
							st.write(f"accepted: {e.get('accepted')}")
							st.write(e.get('text'))


st.caption("Lưu ý: giao diện gọi các lệnh trong rag.py; không hiển thị API key hoặc nội dung .env")
