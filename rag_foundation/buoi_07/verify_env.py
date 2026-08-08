import importlib
import json
import sys
from pathlib import Path

REQ_FILE = Path(__file__).resolve().parent / 'requirements.txt'

packages = [
    ('streamlit', 'streamlit'),
    ('google-genai', 'google.genai'),
    ('chromadb', 'chromadb'),
    ('python-dotenv', 'dotenv'),
]

report = {'packages': {}, 'requirements_file': str(REQ_FILE)}

for pkg_name, import_path in packages:
    info = {'installed': False, 'version': None}
    try:
        mod = importlib.import_module(import_path)
        info['installed'] = True
        ver = getattr(mod, '__version__', None) or getattr(mod, 'version', None)
        if ver is None:
            try:
                import pkg_resources

                ver = pkg_resources.get_distribution(pkg_name).version
            except Exception:
                ver = None
        info['version'] = ver
    except Exception as e:
        info['error'] = str(e)
    report['packages'][pkg_name] = info

print(json.dumps(report))
sys.exit(0)
