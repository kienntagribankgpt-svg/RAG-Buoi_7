import unittest
from pathlib import Path
import tempfile
import shutil
import json
import math

# chromadb will be faked below; do not import real chromadb here
import importlib.util
from pathlib import Path as _P

# import rag.py by path to avoid package path issues
# locate rag.py by searching upward
_p = _P(__file__).resolve()
RAG_PY = None
for i in range(6):
    cand = _p.parents[i] / "rag.py"
    if cand.exists():
        RAG_PY = cand
        break
if RAG_PY is None:
    raise FileNotFoundError("could not locate rag.py for tests")
spec = importlib.util.spec_from_file_location("rag_module", str(RAG_PY))
rag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag)

# --- Fake Chroma module to avoid file locks and external dependencies ---
import types, sys


def _make_fake_chroma_module():
    mod = types.ModuleType("chromadb")

    class Collection:
        def __init__(self, name, metadata):
            self.name = name
            self.metadata = metadata
            self._ids = []
            self._docs = []
            self._embeddings = []
            self._metadatas = []

        def upsert(self, ids, documents, embeddings, metadatas):
            # replace existing ids or append
            for i, _id in enumerate(ids):
                if _id in self._ids:
                    idx = self._ids.index(_id)
                    self._docs[idx] = documents[i]
                    self._embeddings[idx] = embeddings[i]
                    self._metadatas[idx] = metadatas[i]
                else:
                    self._ids.append(_id)
                    self._docs.append(documents[i])
                    self._embeddings.append(embeddings[i])
                    self._metadatas.append(metadatas[i])

        def count(self):
            return len(self._ids)

        def get(self, include=None):
            return {"ids": self._ids, "documents": self._docs, "metadatas": self._metadatas}

        def query(self, query_embeddings=None, n_results=5, include=None):
            q = query_embeddings[0]
            # compute cosine distance: 1 - (dot/(||a||*||b||))
            def cosdist(a, b):
                import math
                dot = sum(x * y for x, y in zip(a, b))
                na = math.sqrt(sum(x * x for x in a))
                nb = math.sqrt(sum(x * x for x in b))
                if na == 0 or nb == 0:
                    return 1.0
                sim = dot / (na * nb)
                return 1.0 - sim

            dists = [cosdist(q, e) for e in self._embeddings]
            # sort by distance ascending
            idxs = sorted(range(len(dists)), key=lambda i: dists[i])[:n_results]
            docs = [self._docs[i] for i in idxs]
            metas = [self._metadatas[i] for i in idxs]
            dd = [dists[i] for i in idxs]
            ids = [self._ids[i] for i in idxs]
            return {"documents": [docs], "metadatas": [metas], "distances": [dd], "ids": [ids]}

    # share server state across PersistentClient instances keyed by path
    _SERVERS = {}

    class PersistentClient:
        def __init__(self, path=None):
            key = str(path) if path is not None else "__default__"
            if key not in _SERVERS:
                _SERVERS[key] = {"collections": {}}
            self._server = _SERVERS[key]

        def list_collections(self):
            return [{"name": n, "metadata": self._server["collections"][n].metadata} for n in self._server["collections"].keys()]

        def create_collection(self, name, embedding_function=None, metadata=None, configuration=None):
            if name in self._server["collections"]:
                raise Exception("Collection already exists")
            col = Collection(name, metadata)
            self._server["collections"][name] = col
            return col

        def get_collection(self, name, embedding_function=None):
            if name not in self._server["collections"]:
                raise Exception("not found")
            return self._server["collections"][name]

        def delete_collection(self, name):
            if name in self._server["collections"]:
                del self._server["collections"][name]

    mod.PersistentClient = PersistentClient
    return mod


_fake_chroma = _make_fake_chroma_module()
sys.modules["chromadb"] = _fake_chroma

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
CHUNKS_SAMPLE = FIXTURES_DIR / "chunks_sample.json"


def make_fake_embed_fn(dim, start=1):
    # returns increasing vectors per call: [start, start+1, ...] in first element, rest tiny values
    counter = {"i": 0}

    def fn(client, model, text, d):
        if d != dim:
            raise ValueError("dim mismatch in embed_fn")
        counter["i"] += 1
        i = counter["i"]
        # create near-orthogonal one-hot-like vectors to avoid proportionality
        vec = [0.0] * d
        idx = (i - 1) % d
        vec[idx] = 1.0
        return vec

    return fn


class TestRagLoader(unittest.TestCase):
    def test_loader_reads_list(self):
        # fixture is a json file; call load_chunks with its parent dir
        chunks, stats = rag.load_chunks(FIXTURES_DIR, strategy="hierarchical")
        self.assertIsInstance(chunks, list)
        self.assertGreater(stats["files_read"], 0)

    def test_loader_reads_chunks_field(self):
        # fixture supports chunks field; ensure selected
        chunks, stats = rag.load_chunks(FIXTURES_DIR, strategy="hierarchical")
        self.assertEqual(stats["valid_chunks"], len(chunks))

    def test_only_select_strategy(self):
        chunks, stats = rag.load_chunks(FIXTURES_DIR, strategy="hierarchical")
        for c in chunks:
            self.assertEqual(c.get("strategy"), "hierarchical")

    def test_missing_field_fails(self):
        rec = {"chunk_id": "x", "strategy": "hierarchical"}
        ok, err = rag.validate_chunk(rec, "t.json", 1)
        self.assertFalse(ok)
        self.assertIn("missing required field", err)

    def test_wrong_type_fails(self):
        rec = {"chunk_id": 123, "strategy": "hierarchical", "source": "s", "page_start": 1, "page_end": 1, "text": "t"}
        ok, err = rag.validate_chunk(rec, "t.json", 1)
        self.assertFalse(ok)
        self.assertIn("field 'chunk_id' must be a string", err)

    def test_boolean_not_allowed_page(self):
        rec = {"chunk_id": "cid", "strategy": "hierarchical", "source": "s", "page_start": True, "page_end": 1, "text": "t"}
        ok, err = rag.validate_chunk(rec, "t.json", 1)
        self.assertFalse(ok)
        self.assertIn("'page_start' must be an integer", err)

    def test_page_start_gt_end_fails(self):
        rec = {"chunk_id": "cid", "strategy": "hierarchical", "source": "s", "page_start": 5, "page_end": 2, "text": "t"}
        ok, err = rag.validate_chunk(rec, "t.json", 1)
        self.assertFalse(ok)
        self.assertIn("page_start", err)

    def test_empty_text_skipped(self):
        # create a temp file
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.json"
            data = [{"chunk_id":"a","strategy":"hierarchical","source":"s","page_start":1,"page_end":1,"text":"   "}]
            p.write_text(json.dumps(data), encoding="utf-8")
            chunks, stats = rag.load_chunks(Path(td), strategy="hierarchical")
            self.assertEqual(stats["empty_text_skipped"], 1)
            self.assertEqual(stats["valid_chunks"], 0)

    def test_duplicate_chunk_id_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.json"
            data = [
                {"chunk_id":"dup","strategy":"hierarchical","source":"s","page_start":1,"page_end":1,"text":"t1"},
                {"chunk_id":"dup","strategy":"hierarchical","source":"s","page_start":2,"page_end":2,"text":"t2"},
            ]
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                rag.load_chunks(Path(td), strategy="hierarchical")

    def test_loader_rejects_non_object_record(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.json"
            data = ["not-an-object"]
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                rag.load_chunks(Path(td), strategy="hierarchical")


class TestRagIndexQuery(unittest.TestCase):
    def setUp(self):
        # temp chroma storage
        self.tmpdir = tempfile.TemporaryDirectory()
        self.storage = Path(self.tmpdir.name)
        # load chunks sample
        with CHUNKS_SAMPLE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # the fixture may include various strategies; select hierarchical
        self.chunks = [c for c in data if c.get("strategy") == "hierarchical"]
        # ensure chunk ids unique
        for i, c in enumerate(self.chunks):
            c["chunk_id"] = f"c{i+1}"
        self.dim = 128
        self.cfg = {
            "GEMINI_API_KEY": "test-key",
            "GEMINI_EMBEDDING_MODEL": "test-model",
            "GEMINI_EMBEDDING_DIM": self.dim,
            "RAG_MAX_DISTANCE": 0.0,
        }

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_index_two_times_idempotent(self):
        embed_fn = make_fake_embed_fn(self.dim)
        ok, msg = rag.index_chunks(self.chunks, self.cfg, embed_fn, self.storage, reset=False)
        self.assertTrue(ok)
        # count
        client = sys.modules['chromadb'].PersistentClient(path=str(self.storage))
        colname = rag.make_collection_name(self.chunks[0].get("strategy"), self.cfg["GEMINI_EMBEDDING_MODEL"], self.dim)
        col = client.get_collection(name=colname, embedding_function=None)
        c1 = col.count()
        # index again
        ok2, msg2 = rag.index_chunks(self.chunks, self.cfg, embed_fn, self.storage, reset=False)
        self.assertTrue(ok2)
        c2 = col.count()
        self.assertEqual(c1, c2)

    def test_collection_identity_changes_with_strategy_model_dim(self):
        name1 = rag.make_collection_name("hierarchical", "m1", 128)
        name2 = rag.make_collection_name("semantic", "m1", 128)
        name3 = rag.make_collection_name("hierarchical", "m2", 128)
        name4 = rag.make_collection_name("hierarchical", "m1", 256)
        self.assertNotEqual(name1, name2)
        self.assertNotEqual(name1, name3)
        self.assertNotEqual(name1, name4)

    def test_missing_api_key_blocks_index(self):
        cfg2 = dict(self.cfg)
        cfg2["GEMINI_API_KEY"] = ""
        embed_fn = make_fake_embed_fn(self.dim)
        ok, msg = rag.index_chunks(self.chunks, cfg2, embed_fn, self.storage)
        self.assertFalse(ok)
        self.assertIn("GEMINI_API_KEY", msg)

    def test_embedding_validation_errors_prevent_upsert(self):
        # embed_fn returns wrong dim
        def bad_embed(client, model, text, d):
            return [0.1] * (d - 1)
        ok, msg = rag.index_chunks(self.chunks, self.cfg, bad_embed, self.storage)
        self.assertFalse(ok)
        self.assertIn("validating embeddings", msg)
        # ensure no collection created
        client = sys.modules['chromadb'].PersistentClient(path=str(self.storage))
        cols = client.list_collections()
        self.assertFalse(any(c.get("name") == rag.make_collection_name(self.chunks[0].get("strategy"), self.cfg["GEMINI_EMBEDDING_MODEL"], self.dim) for c in cols))

    def test_query_insufficient_evidence_blocks_generation(self):
        # create collection with embeddings
        embed_fn = make_fake_embed_fn(self.dim)
        ok, msg = rag.index_chunks(self.chunks, self.cfg, embed_fn, self.storage, reset=True)
        self.assertTrue(ok)
        # set RAG_MAX_DISTANCE tiny (0) so only exact match accepted
        cfg2 = dict(self.cfg)
        cfg2["RAG_MAX_DISTANCE"] = 0.0
        # q_embed_fn returns vector far from any chunk (e.g., high negative)
        def q_embed(client, model, text, d):
            return [-100.0] + [0.0] * (d - 1)

        def gen_fn(prompt):
            raise AssertionError("generation should not be called when insufficient evidence")

        res = rag.query_with_injected("some question", 3, cfg2, q_embed, gen_fn, self.storage, "hierarchical")
        self.assertEqual(res["status"], "insufficient_evidence")

    def test_query_accepted_evidence_triggers_generation_once_and_prompt_contains_question_and_evidence(self):
        embed_fn = make_fake_embed_fn(self.dim)
        ok, msg = rag.index_chunks(self.chunks, self.cfg, embed_fn, self.storage, reset=True)
        self.assertTrue(ok)
        # choose q_embed to match first chunk exactly
        # because embed_fn produced vectors increasing per call starting at 1, first chunk has vector starting 1
        def q_embed(client, model, text, d):
            return [1.0] + [0.001] * (d - 1)

        seen = {}

        def gen_fn(prompt):
            seen['prompt'] = prompt
            return "Answer referencing [E1] and [E99]"

        cfg2 = dict(self.cfg)
        cfg2["RAG_MAX_DISTANCE"] = 0.5  # accept close match only
        res = rag.query_with_injected("What is X?", 2, cfg2, q_embed, gen_fn, self.storage, "hierarchical")
        self.assertEqual(res["status"], "answered")
        self.assertIn("What is X?", seen['prompt'])
        # prompt should contain accepted evidence only (E1)
        self.assertIn("---E1---", seen['prompt'])
        self.assertNotIn("---E2---", seen['prompt'])
        # citation mapping: E1 mapped, E99 removed with warning
        self.assertEqual(len(res["citations"]), 1)
        self.assertTrue(any("unknown citation label" in w for w in res["warnings"]))

    def test_generation_exception_results_in_retrieval_only(self):
        embed_fn = make_fake_embed_fn(self.dim)
        ok, msg = rag.index_chunks(self.chunks, self.cfg, embed_fn, self.storage, reset=True)
        self.assertTrue(ok)

        def q_embed(client, model, text, d):
            return [1.0] + [0.001] * (d - 1)

        def gen_fn(prompt):
            raise RuntimeError("boom")

        cfg2 = dict(self.cfg)
        cfg2["RAG_MAX_DISTANCE"] = 0.1
        res = rag.query_with_injected("Q", 2, cfg2, q_embed, gen_fn, self.storage, "hierarchical")
        self.assertEqual(res["status"], "retrieval_only")
        self.assertTrue(res["warnings"])

    def test_generation_empty_text_becomes_retrieval_only(self):
        embed_fn = make_fake_embed_fn(self.dim)
        ok, msg = rag.index_chunks(self.chunks, self.cfg, embed_fn, self.storage, reset=True)
        self.assertTrue(ok)

        def q_embed(client, model, text, d):
            return [1.0] + [0.001] * (d - 1)

        def gen_fn(prompt):
            return "   "

        cfg2 = dict(self.cfg)
        cfg2["RAG_MAX_DISTANCE"] = 0.1
        res = rag.query_with_injected("Q", 2, cfg2, q_embed, gen_fn, self.storage, "hierarchical")
        self.assertEqual(res["status"], "retrieval_only")

    def test_result_contains_required_fields(self):
        embed_fn = make_fake_embed_fn(self.dim)
        ok, msg = rag.index_chunks(self.chunks, self.cfg, embed_fn, self.storage, reset=True)
        self.assertTrue(ok)

        def q_embed(client, model, text, d):
            return [1.0] + [0.001] * (d - 1)

        def gen_fn(prompt):
            return "Answer [E1]"

        cfg2 = dict(self.cfg)
        cfg2["RAG_MAX_DISTANCE"] = 0.1
        res = rag.query_with_injected("Q", 2, cfg2, q_embed, gen_fn, self.storage, "hierarchical")
        for k in ("status", "answer", "evidence", "citations", "warnings", "collection", "strategy", "top_k"):
            self.assertIn(k, res)


if __name__ == "__main__":
    unittest.main()
