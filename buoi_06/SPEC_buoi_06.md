## Workspace
Chỉ được phép đọc:
- RAG/rag_foundation/buoi_05/output/chunks/
- RAG/rag_foundation/buoi_05/.venv/
- RAG/rag_foundation/buoi_06/

Không đọc:
- source code của Buổi 5
- README các buổi trước
- notebook, git history, các thư mục khác
Buổi 5 là black box. Không reverse engineering.

## Python
Sử dụng đúng interpreter trong: RAG/rag_foundation/buoi_05/.venv/
Không tạo virtual environment mới.

## Package
Chỉ cài: streamlit, google-genai, chromadb, psycopg, python-dotenv
Không cài framework khác.

## Coding Style
Ưu tiên: ít file, ít class, ít function, code dễ đọc.
Không tạo: repository pattern, service layer, dependency injection, factory, plugin.

## Scope & Error Handling
Chỉ cần: index, retrieval, answer, streamlit.
Try/except tối thiểu. Không cần: retry, logging, monitoring.

## Security & Code Size
Không in: API Key, password, secret.
Mục tiêu khoảng 300-500 dòng Python.
