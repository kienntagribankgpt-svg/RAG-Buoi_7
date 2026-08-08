# SPEC_buoi_07

## Workspace
- Readable: `rag_foundation/buoi_05/output/chunks/`, `rag_foundation/buoi_05/.venv/`, `rag_foundation/buoi_06/`, `rag_foundation/buoi_07/`.
- Writable: `rag_foundation/buoi_07/` only.
- Do not modify Buổi 05 or Buổi 06 content.

## Python
- Use the existing `.venv` created in `rag_foundation/buoi_05/` for running scripts.
- Do not create a new virtual environment in this step.

## Input
- The primary input is the JSON files located in `buoi_05/output/chunks/`.
- Buổi 05 is considered the prepared data source. Do not perform OCR, PDF parsing, or re-chunking in this step.

## Packages
- Only the packages listed in `requirements.txt` may be used for implementation.

## Pipeline (high level)
- validate
- embedding
- Chroma persistent index
- retrieval
- confidence gate
- generation
- citation
- Streamlit UI
- unit tests (offline)

Implementation notes:
- Implement each stage incrementally in later steps. Do not implement pipeline logic in this scaffold.

## Data Contract
Each chunk must include the following fields:
- `chunk_id` (string)
- `strategy` (string)
- `source` (string)
- `page_start` (int)
- `page_end` (int)
- `text` (string)

## Index Contract
- Each `strategy` maps to one collection or logical index.
- The embedding model and vector dimension used for indexing and querying must match.
- Use real embeddings (no synthetic or random vectors) when running the index stage.
- Reject vectors containing NaN, Infinity, boolean values, or exact zero-vectors.
- Use Chroma cosine similarity; set `embedding_function=None` and pass precomputed vectors to Chroma's `add`.
- Index operations should be idempotent where possible and expose a read-only `status()`.
- Validate embeddings before resetting/upserting index data.

## Retrieval Contract
- Retrieval must return real evidence text and metadata from the indexed source.
- Each retrieval must include a `distance` (or similarity score).
- Only evidence that meets a configurable similarity threshold is allowed to be passed to the generation stage.
- If evidence is below threshold, skip generation and surface warnings.

## Citation Contract
- Citations must be derived from metadata provided in the source chunks.
- Do not accept citations that are invented by the LLM; treat any LLM-only citation as untrusted and surface a warning.
- Results must include a `citations` list and a `warnings` list when appropriate. Code should map evidence labels into citation objects using real `source`, `page_start`, and `chunk_id`.

## Security
- Do not expose secrets in logs, UI, or test output. Use `.env` for secrets and ensure `.gitignore` excludes it.

## Testing
- Provide unit tests with mocked embedding and generation APIs.
- Use temporary directories for storage in tests and avoid network access and real API keys in CI tests.

## Coding Style
- Keep the code small and focused: prefer a few small functions over many classes.
- Avoid complex architectural patterns for this exercise.
