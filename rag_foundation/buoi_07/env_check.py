import os, json
from pathlib import Path

env_path = Path(__file__).parent / '.env'
required = [
    'GEMINI_API_KEY',
    'GEMINI_EMBEDDING_MODEL',
    'GEMINI_EMBEDDING_DIM',
    'GEMINI_GENERATION_MODEL',
    'DEFAULT_TOP_K',
    'RAG_MAX_DISTANCE',
]
res = {'env_exists': env_path.exists(), 'present': [], 'missing': []}
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k=line.split('=',1)[0].strip()
                res['present'].append(k)
for k in required:
    if k not in res['present']:
        res['missing'].append(k)
print(json.dumps(res, indent=2))
