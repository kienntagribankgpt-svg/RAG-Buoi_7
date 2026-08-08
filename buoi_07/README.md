Buổi 07 — RAG Workshop (Hướng dẫn sử dụng & nghiệm thu)

Mục tiêu
- Xây dựng các bước RAG cơ bản: loader/validator, embedding (Gemini), Chroma persistent index, retrieval, confidence gate, generation và mapping citation. Cung cấp CLI và giao diện Streamlit, cùng bộ unittest offline.

Quan hệ với Buổi 05 / Buổi 06
- Dữ liệu đầu vào (chunks) được chuẩn bị trong Buổi 05: [rag_foundation/buoi_05/output/chunks/](buoi_05/output/chunks/)
- Buổi 06 chứa các bước tiền xử lý khác — không sửa Buổi 05/06 trong bước này.

Sơ đồ pipeline (tóm tắt)
- validate → embedding → Chroma (persistent) → retrieval → confidence gate → generation → citation → UI

Cấu trúc thư mục
- `rag.py`: CLI & helpers (loader, index, query). 
- `app.py`: Streamlit UI (gọi CLI `rag.py`).
- `tests/`: unittest offline với mock embedding/generation và fake Chroma.
- `storage/`: nơi Chroma persistent mặc định (bị `.gitignore`).
- `.env.example`: mẫu biến môi trường.

Điều kiện đầu vào
- JSON chunk files trong `rag_foundation/buoi_05/output/chunks/` theo contract: `chunk_id, strategy, source, page_start, page_end, text`.

Cách dùng môi trường (Virtualenv Buổi 05)
- Sử dụng Python interpreter trong `rag_foundation/buoi_05/.venv/` khi chạy các lệnh sau.

Cài requirements
Windows PowerShell
```powershell
& "rag_foundation/buoi_05/.venv/Scripts/python.exe" -m pip install -r rag_foundation/buoi_07/requirements.txt
```
Linux/macOS
```bash
rag_foundation/buoi_05/.venv/bin/python -m pip install -r rag_foundation/buoi_07/requirements.txt
```

Tạo `.env`
- Sao chép `rag_foundation/buoi_07/.env.example` thành `rag_foundation/buoi_07/.env` và điền `GEMINI_API_KEY` khi cần chạy embedding/generation thật.
- `.env` đã được thêm vào `.gitignore` — không commit file này.

Giải thích biến môi trường (ở `.env`)
- `GEMINI_API_KEY`: (bắt buộc cho embedding/generation thực tế). Nếu thiếu, CLI `index`/`query` sẽ báo lỗi và không gọi API.
- `GEMINI_EMBEDDING_MODEL`: tên model embedding (ví dụ `gemini-embedding-2`).
- `GEMINI_EMBEDDING_DIM`: kích thước vector embedding (ví dụ `768`).
- `GEMINI_GENERATION_MODEL`: model generation (ví dụ `gemini-3.5-flash-lite`).
- `DEFAULT_TOP_K`: mặc định top-k cho truy vấn.
- `RAG_MAX_DISTANCE`: ngưỡng khoảng cách (cosine distance) để chấp nhận evidence.

Lệnh CLI (tóm tắt)
- Validate chunks (đọc từ buoi_05 default hoặc `--path`):
	- `python rag.py validate --strategy hierarchical [--path <dir_or_file>]`
- Status (read-only, không tạo collection):
	- `python rag.py status --strategy hierarchical`
- Index (tạo/update collection). `--reset` xóa collection đích sau khi embeddings được xác thực:
	- `python rag.py index --strategy hierarchical [--path <dir_or_file>] [--reset]`
- Query (retrieval + generation):
	- `python rag.py query --strategy hierarchical --top-k 5 --question "<text>"`

Lệnh chạy unittest (offline, no API keys)
Windows
```powershell
& "rag_foundation/buoi_05/.venv/Scripts/python.exe" -m unittest discover -s rag_foundation/buoi_07/tests -v
```
Linux/macOS
```bash
rag_foundation/buoi_05/.venv/bin/python -m unittest discover -s rag_foundation/buoi_07/tests -v
```

Lệnh chạy Streamlit UI
Windows
```powershell
& "rag_foundation/buoi_05/.venv/Scripts/python.exe" -m streamlit run rag_foundation/buoi_07/app.py
```
Linux/macOS
```bash
rag_foundation/buoi_05/.venv/bin/python -m streamlit run rag_foundation/buoi_07/app.py
```

Giải thích khái niệm
- `strategy`: cách chia/chọn chunk (fixed-size / hierarchical / semantic). Mỗi strategy dùng collection riêng.
- `embedding model`: model dùng để tạo vector (phải khớp giữa index và query).
- `embedding dimension`: độ dài vector; collection identity phụ thuộc vào dim.
- `collection identity`: tên collection được sinh từ `strategy`, `embedding_model` và `dim` (sha1). Đảm bảo tách biệt giữa cấu hình khác nhau.
- `top-k`: số evidence trả về tối đa.
- `cosine distance`: sử dụng `1 - cosine_similarity` làm khoảng cách; nhỏ hơn là tốt hơn. `RAG_MAX_DISTANCE` so sánh với khoảng cách này.
- `confidence gate`: evidence chỉ được đưa vào generation khi `distance <= RAG_MAX_DISTANCE`.
- `retrieval-only`: trạng thái trả về khi generation không được gọi hoặc thất bại; vẫn trả evidence và warnings.
- `citation`: mapping các label `[E1]` sang metadata thực (source, page range, chunk_id); LLM-invented label sẽ bị loại và tạo warning.

Manual test questions (thủ công)
- A (có khả năng thuộc tài liệu): `Cơ cấu lại thời hạn trả nợ được quy định như thế nào?`
- B (có khả năng thuộc tài liệu): `Việc phân loại nợ và trích lập dự phòng được thực hiện như thế nào?`
- C (ngoài phạm vi): `Ngân hàng nào có lãi suất tiết kiệm cao nhất hôm nay?`

Kỳ vọng cho C
- Nếu evidence không đạt threshold thì generation không được gọi và CLI trả:
	`Không tìm thấy đủ thông tin liên quan trong tài liệu đã cung cấp.`
- Không bịa tên ngân hàng hoặc lãi suất.

Troubleshooting (tổng hợp)
- Thiếu package: kiểm tra interpreter là `rag_foundation/buoi_05/.venv` và cài `requirements.txt`.
- Sai interpreter: chạy bằng đường dẫn Python trong Buổi 05 venv.
- Thiếu API key: điền `GEMINI_API_KEY` vào `.env`; nếu không có key, không chạy `index`/`query` thật.
- Collection rỗng: chạy `status` để xem `Collection record count`, nếu 0 thì chạy `index`.
- Model/dimension mismatch: `status` sẽ báo `collection metadata` và `index` sẽ bị chặn nếu mismatch.
- JSON lỗi: `validate` sẽ báo file/record lỗi.
- Embedding lỗi / rate limit: `index` sẽ abort và không xóa collection hiện hữu; xem stderr để biết chi tiết.

Giới hạn của demo
- Không dùng reranker, hybrid search, hoặc OCR ở bước này.
- Không dùng RBAC hay deployment.
- Đây là demo — threshold `RAG_MAX_DISTANCE` cần điều chỉnh cho dataset thực.

Cảnh báo vận hành
- Không dùng nội dung nhạy cảm hoặc bí mật làm input cho dịch vụ bên ngoài.
- Kết quả không phải tư vấn pháp lý; kiểm tra chuyên gia khi cần.

---
Xem `SPEC_buoi_07.md` để biết chi tiết các ràng buộc và hợp đồng dữ liệu.

