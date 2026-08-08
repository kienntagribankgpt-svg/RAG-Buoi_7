import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_DIR = ROOT / 'buoi_05' / 'output' / 'chunks'
REPORT = Path(__file__).resolve().parent / 'chunks_report.json'

report = {
    'total_files': 0,
    'files': [],
    'strategy_counts': {},
    'total_valid_chunks': 0,
}

if not CHUNKS_DIR.exists():
    print(json.dumps({'error': f'chunks dir missing: {CHUNKS_DIR}'}))
    raise SystemExit(1)

files = sorted([p for p in CHUNKS_DIR.glob('*.json') if p.is_file()])
report['total_files'] = len(files)

for p in files:
    entry = {'name': str(p.name), 'size': p.stat().st_size, 'valid_json': False, 'top_type': None, 'top_keys': None, 'sample_fields_present': {}, 'num_chunks': 0}
    try:
        text = p.read_text(encoding='utf-8')
        data = json.loads(text)
        entry['valid_json'] = True
        if isinstance(data, list):
            entry['top_type'] = 'list'
            entry['num_chunks'] = len(data)
            sample = data[0] if data else None
        elif isinstance(data, dict):
            entry['top_type'] = 'object'
            entry['top_keys'] = list(data.keys())
            # try to find list of chunks under common keys
            if 'chunks' in data and isinstance(data['chunks'], list):
                sample_list = data['chunks']
            elif 'fixed' in data and isinstance(data['fixed'], list):
                sample_list = data['fixed']
            else:
                # try first list value
                sample_list = None
                for v in data.values():
                    if isinstance(v, list):
                        sample_list = v
                        break
            entry['num_chunks'] = len(sample_list) if sample_list is not None else 0
            sample = sample_list[0] if sample_list else None
        else:
            entry['top_type'] = type(data).__name__
            sample = None

        # check sample fields
        fields = ['chunk_id', 'strategy', 'source', 'page_start', 'page_end', 'text']
        if isinstance(sample, dict):
            for f in fields:
                entry['sample_fields_present'][f] = f in sample
                if f == 'strategy' and f in sample:
                    strat = sample.get('strategy')
                    report['strategy_counts'][str(strat)] = report['strategy_counts'].get(str(strat), 0) + 1
            report['total_valid_chunks'] += 1
        else:
            for f in fields:
                entry['sample_fields_present'][f] = False

    except Exception as e:
        entry['error'] = str(e)
    report['files'].append(entry)

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps({'status': 'ok', 'report_file': str(REPORT)}))
