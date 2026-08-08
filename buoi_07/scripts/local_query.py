from pathlib import Path
import os, json, math
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / '.env')
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag import load_chunks

cfg = {}
cfg['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
cfg['GEMINI_EMBEDDING_MODEL'] = os.getenv('GEMINI_EMBEDDING_MODEL') or 'gemini-embedding-2'
cfg['GEMINI_EMBEDDING_DIM'] = int(os.getenv('GEMINI_EMBEDDING_DIM') or 768)
cfg['RAG_MAX_DISTANCE'] = float(os.getenv('RAG_MAX_DISTANCE') or 0.5)

chunks, stats = load_chunks(None, strategy='fixed-size')
print('loaded chunks:', len(chunks))

import google.genai as genai

def embed_text(text):
    client = genai.Client(api_key=cfg['GEMINI_API_KEY'])
    resp = client.models.embed_content(model=cfg['GEMINI_EMBEDDING_MODEL'], contents=[text], config={'output_dimensionality': cfg['GEMINI_EMBEDDING_DIM']})
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

# compute embeddings for chunks
embs = []
for c in chunks:
    inp = f"title: {c.get('source')} | text: {c.get('text')}"
    emb = embed_text(inp)
    embs.append(emb)

# sample question
question = 'Nội dung chính của tài liệu là gì?'
q_inp = f"task: question answering | query: {question}"
q_emb = embed_text(q_inp)

# cosine distance function
def cosine_distance(a,b):
    # return 1 - cosine_similarity
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na==0 or nb==0:
        return 1.0
    cos = dot/(na*nb)
    return 1.0 - cos

# compute distances
scores = []
for idx, (c, emb) in enumerate(zip(chunks, embs), start=1):
    dist = cosine_distance(q_emb, emb)
    scores.append((idx, dist, c))

scores.sort(key=lambda x: x[1])

# build evidence
evidence = []
for i, (idx, dist, c) in enumerate(scores[:3], start=1):
    ev = {
        'evidence_id': f'E{i}',
        'text': c.get('text'),
        'source': c.get('source'),
        'page_start': c.get('page_start'),
        'page_end': c.get('page_end'),
        'chunk_id': c.get('chunk_id'),
        'distance': float(dist),
        'accepted': float(dist) <= float(cfg['RAG_MAX_DISTANCE'])
    }
    evidence.append(ev)

accepted = [e for e in evidence if e['accepted']]

# simple generation using accepted evidence
if not accepted:
    result = {'status':'insufficient_evidence','answer':'Không tìm thấy đủ thông tin liên quan trong tài liệu đã cung cấp.','evidence':evidence,'citations':[]}
else:
    # generate a simple answer referencing E1
    answer_text = 'Tài liệu chính nói về ... [E1]'
    # map citation
    accepted_map = {e['evidence_id']:e for e in accepted}
    found_labels = ['1'] if '[E1]' in answer_text else []
    citations = []
    replaced = answer_text
    for lab in found_labels:
        label = f'E{lab}'
        ev = accepted_map.get(label)
        if ev:
            ps = ev['page_start']; pe = ev['page_end']
            if ps==pe:
                page_str = f'tr. {ps}'
            else:
                page_str = f'tr. {ps}-{pe}'
            display = f"[Nguồn: {ev['source']}, {page_str}, chunk: {ev['chunk_id']}]"
            replaced = replaced.replace(f'[{label}]', display, 1)
            citations.append({'evidence_id': label, 'source': ev['source'], 'page_start': ev['page_start'], 'page_end': ev['page_end'], 'chunk_id': ev['chunk_id'], 'display': display})
    result = {'status':'answered','answer':replaced,'evidence':evidence,'citations':citations}

print(json.dumps(result, ensure_ascii=False, indent=2))
