"""RAG Buổi 07 — loader & validator (Step 04)

This module implements a filesystem-backed JSON chunk loader and
validator used by the Buổi 07 exercises. It intentionally avoids any
network, embedding, vector store or LLM calls.

Public functions added in this step:
- `load_chunks(input_dir=None, strategy='hierarchical')`
- `validate_chunk(record, file_name, record_index)`

CLI:
- `python rag.py validate --strategy hierarchical [--path <path>]`

Paths are computed relative to this file using `Path(__file__).resolve()` so
the loader does not depend on the current working directory.
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import json
import argparse


# --- Paths / constants -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
# buoi_05 is a sibling directory to buoi_07 under rag_foundation
DEFAULT_INPUT_DIR = BASE_DIR.parent / "buoi_05" / "output" / "chunks"

ALLOWED_STRATEGIES = {"fixed-size", "semantic", "hierarchical"}


# --- Validation helpers -----------------------------------------------
def _is_int_but_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_chunk(record: Dict[str, Any], file_name: str, record_index: int) -> Tuple[bool, str]:
    """Validate a single chunk record.

    Returns (True, None) when valid, or (False, "error message") when
    invalid. This function does not raise so callers can aggregate errors
    and decide how to proceed.
    """
    # record must be a dict
    if not isinstance(record, dict):
        return False, f"record at position {record_index} in {file_name} is not a JSON object"

    # required keys
    required = ["chunk_id", "strategy", "source", "page_start", "page_end", "text"]
    for k in required:
        if k not in record:
            return False, f"missing required field '{k}' in {file_name} record {record_index}"

    # types and content rules
    for field in ("chunk_id", "strategy", "source", "text"):
        if not isinstance(record.get(field), str):
            return False, f"field '{field}' must be a string in {file_name} record {record_index}"
        if field in ("chunk_id", "strategy", "source") and record.get(field).strip() == "":
            return False, f"field '{field}' must not be empty after strip() in {file_name} record {record_index}"

    strategy = record.get("strategy").strip()
    if strategy not in ALLOWED_STRATEGIES:
        return False, f"invalid strategy '{strategy}' in {file_name} record {record_index}; allowed: {sorted(ALLOWED_STRATEGIES)}"

    # page numbers
    ps = record.get("page_start")
    pe = record.get("page_end")
    if not _is_int_but_not_bool(ps):
        return False, f"'page_start' must be an integer >=1 (not boolean) in {file_name} record {record_index}"
    if not _is_int_but_not_bool(pe):
        return False, f"'page_end' must be an integer >=1 (not boolean) in {file_name} record {record_index}"
    if ps < 1 or pe < 1:
        return False, f"'page_start' and 'page_end' must be >= 1 in {file_name} record {record_index}"
    if ps > pe:
        return False, f"'page_start' ({ps}) > 'page_end' ({pe}) in {file_name} record {record_index}"

    # text presence and type handled above; empty text will be handled by caller
    return True, None


def _read_json_file(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"cannot read file {path}: {e}")
    try:
        return json.loads(text)
    except Exception as e:
        raise ValueError(f"invalid JSON in {path}: {e}")


def load_chunks(input_dir: Path = None, strategy: str = "hierarchical") -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Load and validate chunks from JSON files in `input_dir`.

    Returns (valid_chunks, stats).

    - `input_dir`: Path to directory containing .json files. If None the
      default Buổi 05 path is used.
    - `strategy`: which strategy to select (one of ALLOWED_STRATEGIES).
    """
    if input_dir is None:
        input_dir = DEFAULT_INPUT_DIR
    input_dir = Path(input_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"input directory not found: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"input path is not a directory: {input_dir}")

    strategy = (strategy or "hierarchical").strip()
    if strategy == "":
        strategy = "hierarchical"
    if strategy not in ALLOWED_STRATEGIES:
        raise ValueError(f"unknown strategy '{strategy}'; allowed: {sorted(ALLOWED_STRATEGIES)}")

    files = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".json"], key=lambda p: p.name)
    if not files:
        raise FileNotFoundError(f"no .json files found in {input_dir}")

    stats = {
        "files_read": 0,
        "total_records": 0,
        "selected_records": 0,
        "empty_text_skipped": 0,
        "valid_chunks": 0,
    }

    valid_chunks: List[Dict[str, Any]] = []
    seen_ids: Dict[str, Tuple[str, int]] = {}

    for file_path in files:
        stats["files_read"] += 1
        data = _read_json_file(file_path)

        # normalize list of records
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            # prefer explicit 'chunks' list
            if "chunks" in data and isinstance(data["chunks"], list):
                records = data["chunks"]
            else:
                # support top-level strategy keys like 'fixed', 'semantic', 'hierarchical', or 'fixed-size'
                top_keys = set(k for k in data.keys() if isinstance(k, str))
                allowed_top = {"fixed", "fixed-size", "semantic", "hierarchical", "chunks"}
                present = top_keys & allowed_top
                if not present:
                    raise ValueError(f"unexpected JSON structure in {file_path}; expected list or object with 'chunks' list or strategy keys (fixed/semantic/hierarchical)")

                # map requested strategy to possible top-level keys
                mapping = {
                    "fixed-size": ["fixed-size", "fixed"],
                    "fixed": ["fixed", "fixed-size"],
                    "semantic": ["semantic"],
                    "hierarchical": ["hierarchical"],
                }
                keys_for_strategy = mapping.get(strategy, [strategy])

                chosen_key = None
                for k in keys_for_strategy:
                    if k in data and isinstance(data[k], list):
                        chosen_key = k
                        break

                if chosen_key is not None:
                    records = data[chosen_key]
                else:
                    # requested strategy not present in this file; no records selected
                    records = []
        else:
            raise ValueError(f"unexpected JSON structure in {file_path}; expected list or object with 'chunks' list")

        for idx, rec in enumerate(records, start=1):
            stats["total_records"] += 1

            # record must be object
            if not isinstance(rec, dict):
                raise ValueError(f"record {idx} in file {file_path.name} is not a JSON object")

            # check presence of strategy and filter by requested strategy
            rec_strategy = rec.get("strategy") if isinstance(rec.get("strategy"), str) else None
            if rec_strategy is None:
                # count but do not select
                continue
            if rec_strategy.strip() != strategy:
                # skip records with different strategy
                continue

            stats["selected_records"] += 1

            # validate record
            ok, err = validate_chunk(rec, file_path.name, idx)
            if not ok:
                raise ValueError(err)

            text = rec.get("text")
            if not isinstance(text, str):
                raise ValueError(f"'text' must be a string in {file_path.name} record {idx}")
            stripped = text.strip()
            if stripped == "":
                stats["empty_text_skipped"] += 1
                continue

            chunk_id = rec.get("chunk_id").strip()
            if chunk_id in seen_ids:
                first_file, first_pos = seen_ids[chunk_id]
                raise ValueError(
                    f"duplicate chunk_id '{chunk_id}': first at {first_file} record {first_pos}; then at {file_path.name} record {idx}"
                )

            seen_ids[chunk_id] = (file_path.name, idx)

            # create a non-mutating copy for downstream use
            out = dict(rec)  # shallow copy
            # allow stripping whitespace around text
            out["text"] = stripped

            valid_chunks.append(out)
            stats["valid_chunks"] += 1

    return valid_chunks, stats


# --- Testable helpers (module-level) ---------------------------------
import hashlib, re, math


def make_collection_name(strategy: str, model: str, dim: int) -> str:
    model_hash = hashlib.sha1(model.encode("utf-8")).hexdigest()[:8]
    name = f"rag-{strategy}-{dim}-{model_hash}"
    name = re.sub(r"[^a-z0-9_-]", "-", name.lower())
    return name


def validate_embeddings(embeddings: List[Any], chunks: List[Dict[str, Any]], dim: int):
    if len(embeddings) != len(chunks):
        raise ValueError(f"number of embeddings ({len(embeddings)}) != number of chunks ({len(chunks)})")
    for i, emb in enumerate(embeddings):
        if not isinstance(emb, (list, tuple)):
            raise ValueError(f"embedding {i} is not a list")
        if len(emb) == 0:
            raise ValueError(f"embedding {i} is empty")
        if len(emb) != dim:
            raise ValueError(f"embedding {i} has length {len(emb)} expected {dim}")
        all_zero = True
        for v in emb:
            if isinstance(v, bool):
                raise ValueError(f"embedding {i} contains boolean value")
            try:
                fv = float(v)
            except Exception:
                raise ValueError(f"embedding {i} element not numeric")
            if math.isnan(fv) or math.isinf(fv):
                raise ValueError(f"embedding {i} contains NaN/Infinity")
            if fv != 0.0:
                all_zero = False
        if all_zero:
            raise ValueError(f"embedding {i} is all zeros")


def index_chunks(chunks: List[Dict[str, Any]], cfg: Dict[str, Any], embed_fn, storage_path: Path, reset: bool = False):
    """Index given chunks into a chroma PersistentClient at storage_path.

    - embed_fn(client, model, text, dim) -> embedding (list)
    - cfg must contain GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL, GEMINI_EMBEDDING_DIM
    Returns (True, message) on success or (False, error_message).
    """
    # minimal cfg checks
    if not cfg.get("GEMINI_API_KEY"):
        return False, "GEMINI_API_KEY missing"
    model = cfg.get("GEMINI_EMBEDDING_MODEL")
    dim = int(cfg.get("GEMINI_EMBEDDING_DIM"))
    strategy = chunks[0].get("strategy") if chunks else "hierarchical"
    collection_name = make_collection_name(strategy, model, dim)

    # prepare chroma client
    import chromadb

    client = chromadb.PersistentClient(path=str(storage_path))

    # create or verify collection metadata
    exists = False
    try:
        exists = any(c.get("name") == collection_name for c in client.list_collections())
    except Exception:
        try:
            _ = client.get_collection(name=collection_name, embedding_function=None)
            exists = True
        except Exception:
            exists = False

    metadata = {
        "strategy": strategy,
        "embedding_model": model,
        "embedding_dim": dim,
        "distance_metric": "cosine",
        "schema_version": 1,
    }

    if exists:
        # inspect existing metadata
        col = client.get_collection(name=collection_name, embedding_function=None)
        existing_meta = None
        try:
            existing_meta = col.metadata
        except Exception:
            existing_meta = None
        if existing_meta:
            for k in ("strategy", "embedding_model", "embedding_dim"):
                if str(existing_meta.get(k)) != str(metadata.get(k)):
                    return False, f"existing collection metadata mismatch on: {k}"

    # if reset requested delete
    if reset and exists:
        try:
            client.delete_collection(collection_name)
            exists = False
        except Exception:
            pass

    # generate embeddings
    gen_client_stub = object()
    embeddings = []
    for c in chunks:
        inp = f"title: {c.get('source')} | text: {c.get('text')}"
        try:
            emb = embed_fn(gen_client_stub, model, inp, dim)
        except Exception as e:
            return False, f"embedding failed for chunk_id={c.get('chunk_id')}: {e}"
        embeddings.append(emb)

    # validate embeddings
    try:
        validate_embeddings(embeddings, chunks, dim)
    except Exception as e:
        return False, f"ERROR validating embeddings: {e}"

    # create collection if not exists
    if not exists:
        col = client.create_collection(name=collection_name, embedding_function=None, metadata=metadata, configuration={"hnsw": {"space": "cosine"}})
    else:
        col = client.get_collection(name=collection_name, embedding_function=None)

    ids = [c["chunk_id"] for c in chunks]
    docs = [c["text"] for c in chunks]
    metadatas = []
    for c in chunks:
        metadatas.append({
            "source": c.get("source"),
            "strategy": c.get("strategy"),
            "page_start": c.get("page_start"),
            "page_end": c.get("page_end"),
            "chunk_id": c.get("chunk_id"),
            "embedding_model": model,
            "embedding_dim": dim,
        })

    try:
        col.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)
    except Exception as e:
        return False, f"ERROR upserting to collection: {e}"

    return True, f"Indexed {len(ids)} records into {collection_name}"


def query_with_injected(question: str, top_k: int, cfg: Dict[str, Any], q_embed_fn, gen_fn, storage_path: Path, strategy: str):
    """Run a retrieval+generation flow using injected embedding and generation functions.

    - q_embed_fn(gen_client, model, prompt, dim) -> vector
    - gen_fn(prompt) -> answer_text (string) or raise
    Returns result dict matching CLI JSON structure or raises ValueError on input errors.
    """
    if not isinstance(question, str) or question.strip() == "":
        raise ValueError("question must be non-empty string")
    if not isinstance(top_k, int) or not (1 <= top_k <= 20):
        raise ValueError("top_k must be integer between 1 and 20")

    # check cfg
    if not cfg.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY missing")

    model = cfg.get("GEMINI_EMBEDDING_MODEL")
    dim = int(cfg.get("GEMINI_EMBEDDING_DIM"))
    collection_name = make_collection_name(strategy, model, dim)

    import chromadb
    client = chromadb.PersistentClient(path=str(storage_path))
    # check collection exists
    cols = client.list_collections()
    if not any(c.get("name") == collection_name for c in cols):
        raise ValueError(f"collection '{collection_name}' does not exist")

    col = client.get_collection(name=collection_name, embedding_function=None)
    # verify metadata
    meta = getattr(col, "metadata", None)
    if not meta:
        raise ValueError("collection metadata missing or incompatible")
    if str(meta.get("strategy")) != str(strategy):
        raise ValueError("collection strategy mismatch")

    # check count
    try:
        count = col.count()
    except Exception:
        try:
            res = col.get(include=["ids"])
            ids = res.get("ids") if isinstance(res, dict) else None
            count = len(ids) if ids else 0
        except Exception:
            count = 0
    if count < 1:
        raise ValueError("collection is empty")

    # create query vector
    q_input = f"task: question answering | query: {question}"
    gen_client_stub = object()
    try:
        q_vec = q_embed_fn(gen_client_stub, model, q_input, dim)
    except Exception as e:
        raise RuntimeError(f"ERROR creating query embedding: {e}")

    # validate vector
    validate_embeddings([q_vec], [{"chunk_id":"__query__"}], dim)

    # retrieval
    n_results = top_k if top_k <= count else count
    res = col.query(query_embeddings=[q_vec], n_results=n_results, include=["documents", "metadatas", "distances", "ids"])
    docs = res.get("documents")
    metas = res.get("metadatas")
    dists = res.get("distances")

    # normalize lists
    try:
        docs_list = docs[0] if isinstance(docs[0], list) else docs
    except Exception:
        docs_list = docs
    try:
        metas_list = metas[0] if isinstance(metas[0], list) else metas
    except Exception:
        metas_list = metas
    try:
        dists_list = dists[0] if isinstance(dists[0], list) else dists
    except Exception:
        dists_list = dists

    evidence = []
    for idx, (doc, meta, dist) in enumerate(zip(docs_list, metas_list, dists_list), start=1):
        ev = {
            "evidence_id": f"E{idx}",
            "text": doc,
            "source": meta.get("source"),
            "page_start": meta.get("page_start"),
            "page_end": meta.get("page_end"),
            "chunk_id": meta.get("chunk_id"),
            "distance": float(dist),
            "accepted": float(dist) <= float(cfg.get("RAG_MAX_DISTANCE", 0.0)),
        }
        evidence.append(ev)

    accepted = [e for e in evidence if e["accepted"]]
    result = {"status": None, "answer": "", "evidence": evidence, "citations": [], "warnings": [], "collection": collection_name, "strategy": strategy, "top_k": top_k}

    if not accepted:
        result["status"] = "insufficient_evidence"
        result["answer"] = "Không tìm thấy đủ thông tin liên quan trong tài liệu đã cung cấp."
        return result

    # build prompt
    accepted_map = {e["evidence_id"]: e for e in accepted}
    prompt_parts = ["Bạn là trợ lý trả lời dựa trên tài liệu cung cấp. Chỉ sử dụng các đoạn evidence được liệt kê bên dưới. Không suy diễn thêm.", f"Question: {question}", "EVIDENCES:"]
    for e in accepted:
        prompt_parts.append(f"---{e['evidence_id']}---")
        prompt_parts.append(e["text"])
        prompt_parts.append(f"---END {e['evidence_id']}---")
    prompt = "\n\n".join(prompt_parts)

    # call generation
    try:
        answer_text = gen_fn(prompt)
    except Exception as e:
        result["status"] = "retrieval_only"
        result["answer"] = "Đã truy xuất được nguồn nhưng chưa thể tạo câu trả lời tổng hợp."
        result["warnings"].append(f"generation failed: {e}")
        return result

    if not isinstance(answer_text, str) or answer_text.strip() == "":
        result["status"] = "retrieval_only"
        result["answer"] = "Đã truy xuất được nguồn nhưng chưa thể tạo câu trả lời tổng hợp."
        return result

    answer = answer_text.strip()
    # citation mapping
    import re
    label_pattern = re.compile(r"\[E(\d+)\]")
    found_labels = label_pattern.findall(answer)
    citations = []
    replaced = answer
    seen_labels = set()
    for lab in found_labels:
        label = f"E{lab}"
        if label in accepted_map and label not in seen_labels:
            ev = accepted_map[label]
            ps = ev["page_start"]
            pe = ev["page_end"]
            if ps == pe:
                page_str = f"tr. {ps}"
            else:
                page_str = f"tr. {ps}-{pe}"
            display = f"[Nguồn: {ev['source']}, {page_str}, chunk: {ev['chunk_id']}]"
            replaced = replaced.replace(f"[{label}]", display, 1)
            citations.append({"evidence_id": label, "source": ev["source"], "page_start": ev["page_start"], "page_end": ev["page_end"], "chunk_id": ev["chunk_id"], "display": display})
            seen_labels.add(label)
        else:
            replaced = replaced.replace(f"[E{lab}]", "", 1)
            result["warnings"].append(f"unknown citation label [E{lab}] removed")

    result["status"] = "answered"
    result["answer"] = replaced
    result["citations"] = citations
    return result


# --- CLI ----------------------------------------------------------------
def _print_summary(chunks: List[Dict[str, Any]], stats: Dict[str, int]) -> None:
    from pprint import pprint

    print("=== Validation summary ===")
    print(json.dumps(stats, indent=2))
    print()
    n = min(3, len(chunks))
    if n:
        print(f"Showing up to {n} sample metadata (no full text):")
        for i in range(n):
            c = chunks[i]
            sample = {
                "chunk_id": c.get("chunk_id"),
                "strategy": c.get("strategy"),
                "source": c.get("source"),
                "page_start": c.get("page_start"),
                "page_end": c.get("page_end"),
            }
            pprint(sample)
    else:
        print("No valid chunks found.")


def _cli_validate(argv=None):
    p = argparse.ArgumentParser(prog="rag.py")
    sub = p.add_subparsers(dest="cmd")

    v = sub.add_parser("validate", help="Load and validate chunks")
    v.add_argument("--strategy", default="hierarchical", help="strategy to select")
    v.add_argument("--path", default=None, help="optional path to chunks directory or file")

    s = sub.add_parser("status", help="Show index status (read-only)")
    s.add_argument("--strategy", default="hierarchical", help="strategy to inspect")
    s.add_argument("--path", default=None, help="optional path to chunks directory or file")

    i = sub.add_parser("index", help="Create or update collection with embeddings")
    i.add_argument("--strategy", default="hierarchical", help="strategy to index")
    i.add_argument("--path", default=None, help="optional path to chunks directory or file")
    i.add_argument("--reset", action="store_true", help="delete target collection before indexing")

    q = sub.add_parser("query", help="Run a retrieval + generation query")
    q.add_argument("--strategy", default="hierarchical", help="strategy to query")
    q.add_argument("--top-k", type=int, default=5, help="top k results to retrieve")
    q.add_argument("--question", required=True, help="question text")
    q.add_argument("--path", default=None, help="optional path to chunks directory or file")

    args = p.parse_args(argv)

    cmd = args.cmd
    if cmd == "validate":
        path = Path(args.path) if args.path else None
        if path and path.exists() and path.is_file() and path.suffix.lower() == ".json":
            input_path = path.parent
        else:
            input_path = Path(path) if path else None
        try:
            chunks, stats = load_chunks(input_path, strategy=args.strategy)
        except Exception as e:
            print(f"ERROR: {e}")
            return
        _print_summary(chunks, stats)
        return

    # shared helpers for status/index
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    def read_config():
        # read and validate env vars
        from os import getenv
        cfg = {}
        cfg["GEMINI_API_KEY"] = getenv("GEMINI_API_KEY")
        cfg["GEMINI_EMBEDDING_MODEL"] = getenv("GEMINI_EMBEDDING_MODEL") or ""
        cfg["GEMINI_EMBEDDING_DIM"] = getenv("GEMINI_EMBEDDING_DIM") or ""
        cfg["GEMINI_GENERATION_MODEL"] = getenv("GEMINI_GENERATION_MODEL") or ""
        cfg["DEFAULT_TOP_K"] = getenv("DEFAULT_TOP_K") or ""
        cfg["RAG_MAX_DISTANCE"] = getenv("RAG_MAX_DISTANCE") or ""

        # type validations
        errors = []
        try:
            cfg["GEMINI_EMBEDDING_DIM"] = int(cfg["GEMINI_EMBEDDING_DIM"])
            if not (128 <= cfg["GEMINI_EMBEDDING_DIM"] <= 3072):
                errors.append("GEMINI_EMBEDDING_DIM must be integer between 128 and 3072")
        except Exception:
            errors.append("GEMINI_EMBEDDING_DIM must be an integer")

        try:
            cfg["DEFAULT_TOP_K"] = int(cfg["DEFAULT_TOP_K"])
            if not (1 <= cfg["DEFAULT_TOP_K"] <= 20):
                errors.append("DEFAULT_TOP_K must be integer between 1 and 20")
        except Exception:
            errors.append("DEFAULT_TOP_K must be an integer")

        try:
            cfg["RAG_MAX_DISTANCE"] = float(cfg["RAG_MAX_DISTANCE"]) if cfg["RAG_MAX_DISTANCE"]!="" else 0.0
            if cfg["RAG_MAX_DISTANCE"] < 0:
                errors.append("RAG_MAX_DISTANCE must be non-negative float")
        except Exception:
            errors.append("RAG_MAX_DISTANCE must be a float")

        for k in ("GEMINI_EMBEDDING_MODEL", "GEMINI_GENERATION_MODEL"):
            if not isinstance(cfg[k], str) or cfg[k].strip() == "":
                errors.append(f"{k} must be a non-empty string")

        if errors:
            raise ValueError("; ".join(errors))

        return cfg

    # collection name helper
    import hashlib, re

    def make_collection_name(strategy: str, model: str, dim: int) -> str:
        model_hash = hashlib.sha1(model.encode("utf-8")).hexdigest()[:8]
        safe_model = re.sub(r"[^a-z0-9_-]", "-", model.lower())
        name = f"rag-{strategy}-{dim}-{model_hash}"
        # ensure allowed chars only
        name = re.sub(r"[^a-z0-9_-]", "-", name.lower())
        return name

    # embedder helper (injectable)
    def default_embed_fn(client, model, text, dim):
        # Use the installed google-genai client's models.embed_content API.
        # The SDK returns an EmbedContentResponse with .embeddings -> [ContentEmbedding(values=[...])]
        resp = None
        try:
            resp = client.models.embed_content(model=model, contents=[text], config={"output_dimensionality": dim})
        except Exception as e:
            # Surface a clear error for callers
            raise RuntimeError(f"embedding API call failed: {e}")

        # Normalize response shapes:
        # - typed response: resp.embeddings -> list[ContentEmbedding] where ContentEmbedding.values is list[float]
        # - dict-like: resp["embeddings"][0]["values"]
        emb = None
        try:
            if hasattr(resp, "embeddings") and resp.embeddings is not None:
                first = resp.embeddings[0]
                # typed model object has .values
                emb = getattr(first, "values", None) or first
            elif isinstance(resp, dict) and "embeddings" in resp and isinstance(resp["embeddings"], list):
                item = resp["embeddings"][0]
                if isinstance(item, dict) and "values" in item:
                    emb = item["values"]
                elif isinstance(item, dict) and "embedding" in item:
                    emb = item["embedding"]
                else:
                    emb = item
            else:
                # last-resort: try common keys
                if isinstance(resp, dict) and "data" in resp and isinstance(resp["data"], list) and len(resp["data"])>0:
                    d0 = resp["data"][0]
                    if isinstance(d0, dict) and "embedding" in d0:
                        emb = d0["embedding"]
        except Exception:
            emb = None

        if emb is None:
            raise ValueError("unexpected embedding response shape from genai SDK")
        return emb

    # generate embeddings for chunks
    def generate_embeddings(chunks: List[Dict[str, Any]], cfg: Dict[str, Any], embed_fn=None):
        from google import genai
        client = genai.Client()
        model = cfg["GEMINI_EMBEDDING_MODEL"]
        dim = cfg["GEMINI_EMBEDDING_DIM"]
        embeddings = []
        for c in chunks:
            inp = f"title: {c.get('source')} | text: {c.get('text')}"
            try:
                emb = (embed_fn or default_embed_fn)(client, model, inp, dim)
            except Exception as e:
                raise RuntimeError(f"embedding failed for chunk_id={c.get('chunk_id')}: {e}")
            embeddings.append(emb)
        return embeddings

    def validate_embeddings(embeddings: List[Any], chunks: List[Dict[str, Any]], dim: int):
        if len(embeddings) != len(chunks):
            raise ValueError(f"number of embeddings ({len(embeddings)}) != number of chunks ({len(chunks)})")
        import math
        for i, emb in enumerate(embeddings):
            if not isinstance(emb, (list, tuple)):
                raise ValueError(f"embedding {i} is not a list")
            if len(emb) == 0:
                raise ValueError(f"embedding {i} is empty")
            if len(emb) != dim:
                raise ValueError(f"embedding {i} has length {len(emb)} expected {dim}")
            all_zero = True
            for v in emb:
                if isinstance(v, bool):
                    raise ValueError(f"embedding {i} contains boolean value")
                try:
                    fv = float(v)
                except Exception:
                    raise ValueError(f"embedding {i} element not numeric")
                if math.isnan(fv) or math.isinf(fv):
                    raise ValueError(f"embedding {i} contains NaN/Infinity")
                if fv != 0.0:
                    all_zero = False
            if all_zero:
                raise ValueError(f"embedding {i} is all zeros")

    # Chroma helpers
    import chromadb

    STORAGE_DIR = Path(__file__).resolve().parent / "storage" / "chroma"

    def get_client():
        return chromadb.PersistentClient(path=str(STORAGE_DIR))

    def collection_exists(client, name):
        # use list_collections to avoid creating
        try:
            cols = client.list_collections()
            if isinstance(cols, list):
                for c in cols:
                    if isinstance(c, dict) and c.get("name") == name:
                        return True
            return False
        except Exception:
            # fallback: try get_collection but do not create
            try:
                _ = client.get_collection(name=name, embedding_function=None)
                return True
            except Exception:
                return False

    def get_collection(client, name):
        return client.get_collection(name=name, embedding_function=None)

    def create_collection(client, name, metadata):
        return client.create_collection(name=name, embedding_function=None, metadata=metadata, configuration={"hnsw": {"space": "cosine"}})

    def delete_collection(client, name):
        # delete only specific collection
        try:
            client.delete_collection(name)
        except Exception:
            # try alternative interface
            try:
                client.reset()  # worst-case not desired
            except Exception:
                raise

    # handle status and index
    if cmd == "status":
        try:
            cfg = read_config()
        except Exception as e:
            print(f"CONFIG ERROR: {e}")
            return

        api_ok = bool(cfg.get("GEMINI_API_KEY"))
        model = cfg.get("GEMINI_EMBEDDING_MODEL")
        dim = cfg.get("GEMINI_EMBEDDING_DIM")
        strategy = args.strategy
        collection_name = make_collection_name(strategy, model, dim)

        print("API Key:", "Có" if api_ok else "Thiếu")
        print("Embedding model:", model)
        print("Embedding dim:", dim)
        print("Strategy:", strategy)
        print("Collection name:", collection_name)

        # check collection existence and count
        client = get_client()
        exists = collection_exists(client, collection_name)
        print("Collection exists:", exists)
        if exists:
            try:
                col = get_collection(client, collection_name)
                try:
                    cnt = col.count()
                except Exception:
                    # fallback: try to get ids length
                    try:
                        res = col.get(include=["ids"])  # may be unsupported
                        ids = res.get("ids") if isinstance(res, dict) else None
                        cnt = len(ids) if ids else "unknown"
                    except Exception:
                        cnt = "unknown"
                print("Collection record count:", cnt)
                # try to print stored metadata if present
                meta = None
                try:
                    meta = col.metadata
                except Exception:
                    try:
                        meta = getattr(col, "get_metadata", lambda: None)()
                    except Exception:
                        meta = None
                print("Collection metadata:", meta)
            except Exception as e:
                print("Could not inspect collection:", e)
        return

    if cmd == "index":
        try:
            cfg = read_config()
        except Exception as e:
            print(f"CONFIG ERROR: {e}")
            return

        if not cfg.get("GEMINI_API_KEY"):
            print("ERROR: GEMINI_API_KEY missing in .env — cannot run index")
            return

        path = Path(args.path) if args.path else None
        if path and path.exists() and path.is_file() and path.suffix.lower() == ".json":
            input_path = path.parent
        else:
            input_path = Path(path) if path else None

        try:
            chunks, stats = load_chunks(input_path, strategy=args.strategy)
        except Exception as e:
            print(f"ERROR loading chunks: {e}")
            return

        if not chunks:
            print("No chunks to index for chosen strategy")
            return

        # generate embeddings (validate all before upsert)
        try:
            embeddings = generate_embeddings(chunks, cfg, embed_fn=None)
        except Exception as e:
            print(f"ERROR generating embeddings: {e}")
            return

        try:
            validate_embeddings(embeddings, chunks, cfg["GEMINI_EMBEDDING_DIM"])
        except Exception as e:
            print(f"ERROR validating embeddings: {e}")
            return

        # prepare Chroma collection
        collection_name = make_collection_name(args.strategy, cfg["GEMINI_EMBEDDING_MODEL"], cfg["GEMINI_EMBEDDING_DIM"])
        metadata = {
            "strategy": args.strategy,
            "embedding_model": cfg["GEMINI_EMBEDDING_MODEL"],
            "embedding_dim": cfg["GEMINI_EMBEDDING_DIM"],
            "distance_metric": "cosine",
            "schema_version": 1,
        }

        client = get_client()
        exists = collection_exists(client, collection_name)
        if exists:
            # verify existing metadata
            try:
                col = get_collection(client, collection_name)
                existing_meta = None
                try:
                    existing_meta = col.metadata
                except Exception:
                    existing_meta = None
                if existing_meta:
                    # check compatibility
                    mismatches = []
                    for k in ("strategy", "embedding_model", "embedding_dim"):
                        if str(existing_meta.get(k)) != str(metadata.get(k)):
                            mismatches.append(k)
                    if mismatches:
                        print("ERROR: existing collection metadata mismatch on:", mismatches)
                        print("Use --reset to remove the incompatible collection and retry")
                        return
            except Exception as e:
                print("ERROR inspecting existing collection:", e)
                return

        # if reset requested, delete collection AFTER embeddings validated
        if args.reset and exists:
            try:
                delete_collection(client, collection_name)
                exists = False
                print("Deleted existing collection (reset)")
            except Exception as e:
                print("ERROR deleting collection:", e)
                return

        # create collection if not exists
        try:
            if not exists:
                col = create_collection(client, collection_name, metadata)
            else:
                col = get_collection(client, collection_name)
        except Exception as e:
            print(f"ERROR creating/getting collection: {e}")
            return

        # perform single upsert with all records
        ids = [c["chunk_id"] for c in chunks]
        docs = [c["text"] for c in chunks]
        metadatas = []
        for c in chunks:
            md = {
                "source": c.get("source"),
                "strategy": c.get("strategy"),
                "page_start": c.get("page_start"),
                "page_end": c.get("page_end"),
                "chunk_id": c.get("chunk_id"),
                "embedding_model": cfg["GEMINI_EMBEDDING_MODEL"],
                "embedding_dim": cfg["GEMINI_EMBEDDING_DIM"],
            }
            metadatas.append(md)

        try:
            col.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)
        except Exception as e:
            print(f"ERROR upserting to collection: {e}")
            return

        print("Indexing complete. Records upserted:", len(ids))
        return

    if cmd == "query":
        # Always emit a single clean JSON object on stdout for Streamlit to parse.
        def _json_exit(obj):
            print(json.dumps(obj, ensure_ascii=False))
            return

        # validate basic inputs
        question = args.question
        if not isinstance(question, str) or question.strip() == "":
            return _json_exit({"status": "error", "error": "question must be a non-empty string"})
        question = question.strip()
        if len(question) > 2000:
            return _json_exit({"status": "error", "error": "question exceeds 2000 characters"})

        top_k = args.top_k
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not (1 <= top_k <= 20):
            return _json_exit({"status": "error", "error": "--top-k must be integer between 1 and 20"})

        strategy = args.strategy
        if strategy not in ALLOWED_STRATEGIES:
            return _json_exit({"status": "error", "error": f"unknown strategy '{strategy}'"})

        # read config
        try:
            cfg = read_config()
        except Exception as e:
            return _json_exit({"status": "error", "error": f"CONFIG ERROR: {e}"})

        if not cfg.get("GEMINI_API_KEY"):
            return _json_exit({"status": "error", "error": "GEMINI_API_KEY missing in .env — cannot run query"})

        # collection name and existence
        collection_name = make_collection_name(strategy, cfg["GEMINI_EMBEDDING_MODEL"], cfg["GEMINI_EMBEDDING_DIM"])
        client = get_client()
        if not collection_exists(client, collection_name):
            return _json_exit({"status": "error", "error": f"collection '{collection_name}' does not exist; run index first"})

        col = get_collection(client, collection_name)
        # verify collection metadata
        try:
            existing_meta = None
            try:
                existing_meta = col.metadata
            except Exception:
                existing_meta = None
            if not existing_meta:
                return _json_exit({"status": "error", "error": "collection metadata missing; incompatible collection"})
            # explicit checks
            if str(existing_meta.get("strategy")) != str(strategy):
                return _json_exit({"status": "error", "error": "collection strategy mismatch; re-index with correct strategy"})
            if str(existing_meta.get("embedding_model")) != str(cfg["GEMINI_EMBEDDING_MODEL"]):
                return _json_exit({"status": "error", "error": "collection embedding_model mismatch; re-index with correct model"})
            if int(existing_meta.get("embedding_dim")) != int(cfg["GEMINI_EMBEDDING_DIM"]):
                return _json_exit({"status": "error", "error": "collection embedding_dim mismatch; re-index with correct dim"})
            if str(existing_meta.get("distance_metric")) != "cosine":
                return _json_exit({"status": "error", "error": "collection distance metric not cosine; incompatible"})
        except Exception as e:
            return _json_exit({"status": "error", "error": f"ERROR inspecting collection metadata: {e}"})

        # ensure collection has at least one record
        try:
            try:
                count = col.count()
            except Exception:
                # fallback to get ids
                try:
                    res = col.get(include=["ids"])
                    ids = res.get("ids") if isinstance(res, dict) else None
                    count = len(ids) if ids else 0
                except Exception:
                    count = 0
            if count < 1:
                return _json_exit({"status": "error", "error": "collection is empty"})
        except Exception as e:
            return _json_exit({"status": "error", "error": f"ERROR checking collection count: {e}"})

        # create query embedding
        from google import genai
        client_gen = genai.Client()
        q_model = cfg["GEMINI_EMBEDDING_MODEL"]
        q_dim = cfg["GEMINI_EMBEDDING_DIM"]
        q_input = f"task: question answering | query: {question}"
        try:
            q_vec = default_embed_fn(client_gen, q_model, q_input, q_dim)
        except Exception as e:
            return _json_exit({"status": "error", "error": f"ERROR creating query embedding: {e}"})

        # validate query vector
        try:
            validate_embeddings([q_vec], [ {"chunk_id":"__query__"} ], q_dim)
        except Exception as e:
            return _json_exit({"status": "error", "error": f"ERROR validating query embedding: {e}"})

        # retrieval
        try:
            # n_results = min(top_k, count)
            n_results = top_k if top_k <= count else count
            res = col.query(query_embeddings=[q_vec], n_results=n_results, include=["documents", "metadatas", "distances", "ids"])
        except Exception as e:
            return _json_exit({"status": "error", "error": f"ERROR querying collection: {e}"})

        # parse retrieval response
        # expected shapes: dict with keys 'documents','metadatas','distances','ids' each a list of lists (per query)
        try:
            docs = res.get("documents") if isinstance(res, dict) else None
            metas = res.get("metadatas") if isinstance(res, dict) else None
            dists = res.get("distances") if isinstance(res, dict) else None
            ids = res.get("ids") if isinstance(res, dict) else None
            if docs is None or metas is None or dists is None:
                raise ValueError("query response missing expected fields")
            # take first query batch
            docs = docs[0] if isinstance(docs[0], list) or True else docs
        except Exception as e:
            # try alternate shape
            try:
                docs = res["documents"]
                metas = res["metadatas"]
                dists = res["distances"]
                ids = res.get("ids")
            except Exception:
                print(f"ERROR parsing query response: {e}")
                return

        # ensure lists
        try:
            docs_list = docs[0] if isinstance(docs[0], list) else docs
        except Exception:
            docs_list = docs
        try:
            metas_list = metas[0] if isinstance(metas[0], list) else metas
        except Exception:
            metas_list = metas
        try:
            dists_list = dists[0] if isinstance(dists[0], list) else dists
        except Exception:
            dists_list = dists
        try:
            ids_list = ids[0] if isinstance(ids and ids[0], list) else ids
        except Exception:
            ids_list = ids

        evidence = []
        for idx, (doc, meta, dist) in enumerate(zip(docs_list, metas_list, dists_list), start=1):
            ev = {
                "evidence_id": f"E{idx}",
                "text": doc,
                "source": meta.get("source"),
                "page_start": meta.get("page_start"),
                "page_end": meta.get("page_end"),
                "chunk_id": meta.get("chunk_id"),
                "distance": float(dist),
                "accepted": float(dist) <= float(cfg["RAG_MAX_DISTANCE"]),
            }
            evidence.append(ev)

        # determine accepted evidence
        accepted = [e for e in evidence if e["accepted"]]
        result = {
            "status": None,
            "answer": "",
            "evidence": evidence,
            "citations": [],
            "warnings": [],
            "collection": collection_name,
            "strategy": strategy,
            "top_k": top_k,
        }

        if not accepted:
            result["status"] = "insufficient_evidence"
            result["answer"] = "Không tìm thấy đủ thông tin liên quan trong tài liệu đã cung cấp."
            return _json_exit(result)

        # build prompt with accepted evidence only
        accepted_map = {e["evidence_id"]: e for e in accepted}
        prompt_parts = []
        prompt_parts.append("Bạn là trợ lý trả lời dựa trên tài liệu cung cấp. Chỉ sử dụng các đoạn evidence được liệt kê bên dưới. Không suy diễn thêm.")
        prompt_parts.append(f"Question: {question}")
        prompt_parts.append("EVIDENCES:")
        for e in accepted:
            prompt_parts.append(f"---{e['evidence_id']}---")
            prompt_parts.append(e["text"])
            prompt_parts.append(f"---END {e['evidence_id']}---")

        prompt = "\n\n".join(prompt_parts)

        # call generation
        gen_model = cfg["GEMINI_GENERATION_MODEL"]
        try:
            gen_client = genai.Client()
            gen_resp = gen_client.models.generate_content(model=gen_model, prompt=prompt)
            # parse response
            answer_text = getattr(gen_resp, "text", None) or (gen_resp.get("text") if isinstance(gen_resp, dict) else None)
            if answer_text is None:
                # try other shapes
                try:
                    answer_text = str(gen_resp)
                except Exception:
                    answer_text = ""
        except Exception as e:
            result["status"] = "retrieval_only"
            result["answer"] = "Đã truy xuất được nguồn nhưng chưa thể tạo câu trả lời tổng hợp."
            result["warnings"].append(f"generation failed: {str(e)}")
            return _json_exit(result)

        if not isinstance(answer_text, str) or answer_text.strip() == "":
            result["status"] = "retrieval_only"
            result["answer"] = "Đã truy xuất được nguồn nhưng chưa thể tạo câu trả lời tổng hợp."
            return _json_exit(result)

        answer = answer_text.strip()

        # citation mapping: find labels like [E1], [E2] in answer
        import re
        label_pattern = re.compile(r"\[E(\d+)\]")
        found_labels = label_pattern.findall(answer)
        citations = []
        replaced = answer
        seen_labels = set()
        for lab in found_labels:
            label = f"E{lab}"
            if label in accepted_map and label not in seen_labels:
                ev = accepted_map[label]
                # create display
                ps = ev["page_start"]
                pe = ev["page_end"]
                if ps == pe:
                    page_str = f"tr. {ps}"
                else:
                    page_str = f"tr. {ps}-{pe}"
                display = f"[Nguồn: {ev['source']}, {page_str}, chunk: {ev['chunk_id']}]"
                # replace first occurrence of [E#] with display
                replaced = replaced.replace(f"[{label}]", display, 1)
                citations.append({
                    "evidence_id": label,
                    "source": ev["source"],
                    "page_start": ev["page_start"],
                    "page_end": ev["page_end"],
                    "chunk_id": ev["chunk_id"],
                    "display": display,
                })
                seen_labels.add(label)
            else:
                # remove label and warn
                replaced = replaced.replace(f"[E{lab}]", "", 1)
                result["warnings"].append(f"unknown citation label [E{lab}] removed")

        result["status"] = "answered"
        result["answer"] = replaced
        result["citations"] = citations
        return _json_exit(result)


if __name__ == "__main__":
    _cli_validate()

