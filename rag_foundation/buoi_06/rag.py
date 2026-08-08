from pathlib import Path
import json
import os
import sqlite3
from typing import Dict, List, Optional

import psycopg
import chromadb
import google.genai as genai
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
CHUNKS_DIR = BASE_DIR.parent / "buoi_05" / "output" / "chunks"
FALLBACK_CHUNK_FILE = BASE_DIR.parent / "buoi_05" / "output" / "chunks_result.json"
DB_PATH = BASE_DIR / "app.db"
CHROMA_DIR = BASE_DIR / "storage" / "chroma"
ENV_FILE = BASE_DIR / ".env"
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "gemini-embedding-2"
GENERATION_MODEL = "gemini-flash-lite-latest"


def load_environment() -> None:
    env_path = ENV_FILE if ENV_FILE.exists() else ENV_FILE.with_suffix(".example")
    load_dotenv(dotenv_path=env_path)


def has_api_key() -> bool:
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def _json_files() -> List[Path]:
    if CHUNKS_DIR.exists() and CHUNKS_DIR.is_dir():
        return sorted(CHUNKS_DIR.glob("*.json"))
    if FALLBACK_CHUNK_FILE.exists():
        return [FALLBACK_CHUNK_FILE]
    return []


def _parse_chunks_from_file(path: Path) -> List[Dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "fixed" in raw:
        items = raw["fixed"]
    elif isinstance(raw, dict) and "chunks" in raw:
        items = raw["chunks"]
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    parsed = []
    for index, chunk in enumerate(items):
        if not isinstance(chunk, dict):
            continue
        parsed.append(
            {
                "chunk_id": str(chunk.get("chunk_id", index)),
                "text": chunk.get("text", ""),
                "metadata": {
                    "source": chunk.get("source", "unknown"),
                    "page_start": chunk.get("page_start"),
                    "page_end": chunk.get("page_end"),
                },
            }
        )
    return parsed


def read_chunks() -> List[Dict]:
    files = _json_files()
    chunks = []
    for path in files:
        chunks.extend(_parse_chunks_from_file(path))
    return chunks


def _connect_sqlite() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chunks ("
        "chunk_id TEXT PRIMARY KEY, text TEXT NOT NULL, metadata TEXT NOT NULL)"
    )
    conn.commit()
    return conn


def _connect_postgres() -> Optional[psycopg.Connection]:
    if not os.getenv("POSTGRES_HOST"):
        return None
    try:
        conn = psycopg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=os.getenv("POSTGRES_DB", "rag_db"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        )
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS chunks ("
                "chunk_id TEXT PRIMARY KEY, text TEXT NOT NULL, metadata TEXT NOT NULL)"
            )
        conn.commit()
        return conn
    except Exception:
        return None


def connect_database():
    pg_conn = _connect_postgres()
    if pg_conn is not None:
        return pg_conn, "postgres"
    return _connect_sqlite(), "sqlite"


def _save_chunks_db(conn, backend: str, chunks: List[Dict]) -> int:
    if not chunks:
        return 0
    prepared = [(c["chunk_id"], c["text"], json.dumps(c["metadata"], ensure_ascii=False)) for c in chunks]
    if backend == "postgres":
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chunks (chunk_id, text, metadata) VALUES (%s, %s, %s) "
                "ON CONFLICT (chunk_id) DO NOTHING",
                prepared,
            )
        conn.commit()
    else:
        conn.executemany(
            "INSERT OR IGNORE INTO chunks (chunk_id, text, metadata) VALUES (?, ?, ?)",
            prepared,
        )
        conn.commit()
    return len(prepared)


def _load_chunks_by_ids(conn, backend: str, chunk_ids: List[str]) -> List[Dict]:
    if not chunk_ids:
        return []
    placeholders = ",".join(["%s"] * len(chunk_ids)) if backend == "postgres" else ",".join(["?"] * len(chunk_ids))
    query = f"SELECT chunk_id, text, metadata FROM chunks WHERE chunk_id IN ({placeholders})"
    params = chunk_ids
    if backend == "sqlite":
        cur = conn.execute(query, params)
        rows = cur.fetchall()
    else:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    result = []
    for row in rows:
        result.append({"chunk_id": row[0], "text": row[1], "metadata": json.loads(row[2])})
    return result


def _db_search(conn, backend: str, question: str, k: int) -> List[Dict]:
    token = f"%{question.replace('%', '%%')}%"
    if backend == "postgres":
        query = (
            "SELECT chunk_id, text, metadata FROM chunks "
            "WHERE text ILIKE %s OR metadata ILIKE %s LIMIT %s"
        )
        params = (token, token, k)
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    else:
        query = (
            "SELECT chunk_id, text, metadata FROM chunks "
            "WHERE text LIKE ? OR metadata LIKE ? LIMIT ?"
        )
        params = (token, token, k)
        rows = conn.execute(query, params).fetchall()
    return [{"chunk_id": row[0], "text": row[1], "metadata": json.loads(row[2])} for row in rows]


def create_genai_client() -> genai.Client:
    return genai.Client()


def _create_chroma_collection():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path="storage/chroma")
    return client.get_or_create_collection(name=COLLECTION_NAME)


def _embed_texts(client: genai.Client, texts: List[str]) -> List[List[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config={"output_dimensionality": 384},
    )
    embeddings: List[List[float]] = []
    items = None
    if hasattr(response, "embeddings"):
        items = response.embeddings
    elif hasattr(response, "embedding"):
        items = response.embedding
    elif isinstance(response, dict):
        if "embeddings" in response:
            items = response["embeddings"]
        elif "embedding" in response:
            items = response["embedding"]

    def _extract_values(item):
        if hasattr(item, "values"):
            return list(item.values)
        if isinstance(item, dict) and "values" in item:
            return list(item["values"])
        if isinstance(item, list):
            return list(item)
        return None

    if isinstance(items, (list, tuple)):
        for item in items:
            vals = _extract_values(item)
            if vals is not None:
                embeddings.append(vals)
    else:
        vals = _extract_values(items)
        if vals is not None:
            embeddings.append(vals)

    if len(embeddings) != len(texts):
        raise RuntimeError(
            f"Embedding count {len(embeddings)} does not match input count {len(texts)}"
        )
    return embeddings


def _add_to_chroma(collection, chunks: List[Dict], embeddings: List[List[float]]) -> int:
    if not chunks or not embeddings:
        return 0
    if hasattr(collection, "count") and collection.count() > 0:
        return 0
    ids = [chunk["chunk_id"] for chunk in chunks]
    docs = [chunk["text"] for chunk in chunks]
    metas = [chunk["metadata"] for chunk in chunks]
    collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)
    return len(ids)


def _count_chroma(collection) -> int:
    if hasattr(collection, "count"):
        return collection.count()
    return 0


def _build_prompt(question: str, documents: List[Dict]) -> str:
    pieces = []
    for doc in documents:
        meta = doc.get("metadata", {})
        source = meta.get("source", "unknown")
        page = meta.get("page_start")
        header = f"Source: {source}" + (f" | Page: {page}" if page is not None else "")
        pieces.append(f"{header}\n{doc.get('text', '')}")
    context = "\n\n---\n\n".join(pieces)
    return (
        "You are a helpful assistant. Use the context below to answer the question directly. "
        "Do not invent facts. If the answer is not contained in the context, say you cannot answer.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )


def _extract_response(response) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text
    if hasattr(response, "text") and response.text:
        return response.text
    if hasattr(response, "output"):
        output = response.output
        if isinstance(output, str):
            return output
        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, dict):
                content = first.get("content")
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    return ""


def index() -> Dict[str, int]:
    load_environment()
    chunks = read_chunks()
    conn, backend = connect_database()
    saved = _save_chunks_db(conn, backend, chunks)
    if backend == "sqlite":
        conn.close()
    chroma_count = 0
    if has_api_key() and chunks:
        client = create_genai_client()
        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        embeddings = []
        for text in documents:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
                config={"output_dimensionality": 384},
            )
            embedding = None
            if hasattr(response, "embedding") and hasattr(response.embedding, "values"):
                embedding = list(response.embedding.values)
            elif hasattr(response, "embeddings") and response.embeddings:
                first = response.embeddings[0]
                if hasattr(first, "values"):
                    embedding = list(first.values)
            elif isinstance(response, dict):
                if "embedding" in response and isinstance(response["embedding"], dict) and "values" in response["embedding"]:
                    embedding = list(response["embedding"]["values"])
                elif "embeddings" in response and isinstance(response["embeddings"], list) and response["embeddings"]:
                    first = response["embeddings"][0]
                    if isinstance(first, dict) and "values" in first:
                        embedding = list(first["values"])
            if embedding is None:
                raise RuntimeError("Unable to parse embedding response from Gemini for a document")
            embeddings.append(embedding)
        collection = _create_chroma_collection()
        chroma_count = _add_to_chroma(collection, chunks, embeddings)
    return {
        "chunks_found": len(chunks),
        "chunks_saved": saved,
        "chroma_indexed": chroma_count,
        "db_backend": backend,
    }


def ask(question: str, k: int = 3) -> Dict:
    load_environment()
    conn, backend = connect_database()
    retrievals: List[Dict] = []
    if has_api_key():
        client = create_genai_client()
        collection = _create_chroma_collection()
        # embed the question
        query_embedding_vector = _embed_texts(client, [question])[0]
        # query chroma for nearest neighbors (omit include to avoid version mismatches)
        results = collection.query(query_embeddings=[query_embedding_vector], n_results=k)
        # prefer ids from the chroma result so we can load canonical text from the DB
        ids = results.get("ids", [[]])[0] if results.get("ids") is not None else []
        docs: List[Dict] = []
        if ids:
            rows = _load_chunks_by_ids(conn, backend, ids)
            for row in rows:
                docs.append({"chunk_id": row["chunk_id"], "text": row["text"], "metadata": row.get("metadata", {})})
        else:
            # fallback: use documents/metadatas returned directly by Chroma
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            for text, meta in zip(documents, metadatas):
                docs.append({"text": text, "metadata": meta})
        if docs:
            prompt = _build_prompt(question, docs)
            response = client.models.generate_content(
                model=GENERATION_MODEL,
                contents=prompt,
            )
            answer = response.text
            if backend == "sqlite":
                conn.close()
            return {"answer": answer, "retrievals": docs}
        retrievals = _db_search(conn, backend, question, k)
    else:
        retrievals = _db_search(conn, backend, question, k)
    if backend == "sqlite":
        conn.close()
    return {"retrievals": retrievals}


def status() -> Dict[str, int]:
    load_environment()
    conn, backend = connect_database()
    if backend == "sqlite":
        row = conn.execute("SELECT COUNT(1) FROM chunks").fetchone()
        count = row[0] if row else 0
        conn.close()
    else:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(1) FROM chunks")
            count = cur.fetchone()[0]
        conn.close()
    collection = _create_chroma_collection()
    chroma_count = _count_chroma(collection)
    return {"documents": count, "chunks_indexed": chroma_count}


if __name__ == "__main__":
    print("Use index(), ask(question, k), and status() from this module.")
