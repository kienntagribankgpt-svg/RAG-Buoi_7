from pathlib import Path
import json, os
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / '.env')
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag import load_chunks, index_chunks, query_with_injected

p = Path(__file__).resolve().parent.parent / 'storage' / 'chroma' / 'test_run'
p.mkdir(parents=True, exist_ok=True)

cfg = {}
cfg['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
cfg['GEMINI_EMBEDDING_MODEL'] = os.getenv('GEMINI_EMBEDDING_MODEL') or 'gemini-embedding-2'
cfg['GEMINI_EMBEDDING_DIM'] = int(os.getenv('GEMINI_EMBEDDING_DIM') or 768)

chunks, stats = load_chunks(None, strategy='fixed-size')
print('chunks:', len(chunks), 'stats:', stats)

import google.genai as genai

def embed_fn(client_stub, model, text, dim):
    client = genai.Client(api_key=cfg['GEMINI_API_KEY'])
    resp = client.models.embed_content(model=model, contents=[text], config={'output_dimensionality': dim})
    # extract values
    if hasattr(resp, 'embeddings') and resp.embeddings:
        first = resp.embeddings[0]
        vals = getattr(first, 'values', None)
        if vals:
            return vals
    if isinstance(resp, dict):
        if 'embeddings' in resp and isinstance(resp['embeddings'], list):
            item = resp['embeddings'][0]
            if isinstance(item, dict) and 'values' in item:
                return item['values']
            if isinstance(item, dict) and 'embedding' in item:
                return item['embedding']
    raise RuntimeError('cannot parse embedding response')

# index first time
try:
    ok, msg = index_chunks(chunks, cfg, embed_fn, p, reset=False)
    print('first index:', ok, msg)
except Exception as e:
    print('first index failed (likely already exists):', e)
# index second time to test idempotency
try:
    ok2, msg2 = index_chunks(chunks, cfg, embed_fn, p, reset=False)
    print('second index:', ok2, msg2)
except Exception as e:
    print('second index attempt failed (exists or other):', e)

# simple gen_fn that composes answer referencing E1
def gen_fn(prompt):
    return 'Tóm tắt: Tài liệu liên quan đến ... [E1]'

res = query_with_injected('Nội dung chính của tài liệu là gì?', 3, cfg, embed_fn, gen_fn, p, 'fixed-size')
print(json.dumps(res, ensure_ascii=False, indent=2))
