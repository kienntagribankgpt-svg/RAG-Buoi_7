import chromadb, json, sys
p = r"d:\du_an_cua_ban\RAG\rag_foundation\buoi_07\storage\chroma"
client = chromadb.PersistentClient(path=p)
cols = client.list_collections()
print(json.dumps(cols, indent=2, ensure_ascii=False))
for c in cols:
    try:
        name = c.get('name') if isinstance(c, dict) else str(c)
        print('--- collection:', name)
        col = client.get_collection(name=name, embedding_function=None)
        meta = getattr(col, 'metadata', None)
        print('metadata:', meta)
        try:
            cnt = col.count()
        except Exception:
            try:
                r = col.get(include=['ids'])
                ids = r.get('ids') if isinstance(r, dict) else None
                cnt = len(ids) if ids else 'unknown'
            except Exception:
                cnt = 'unknown'
        print('count:', cnt)
    except Exception as e:
        print('error inspecting', c, str(e))
