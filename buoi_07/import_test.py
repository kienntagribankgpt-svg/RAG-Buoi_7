import json
import importlib

checks = {}

def check(name, import_path, attr_names=None):
    info = {'ok': False, 'version': None, 'error': None}
    try:
        mod = importlib.import_module(import_path)
        info['ok'] = True
        ver = None
        for a in (attr_names or ['__version__', 'version']):
            ver = getattr(mod, a, None)
            if ver:
                break
        if ver is None:
            try:
                import pkg_resources
                ver = pkg_resources.get_distribution(name).version
            except Exception:
                ver = None
        info['version'] = ver
    except Exception as e:
        info['error'] = str(e)
    checks[name] = info

packages = [
    ('streamlit', 'streamlit'),
    ('chromadb', 'chromadb'),
    ('python-dotenv', 'dotenv'),
]
for pkg in packages:
    check(pkg[0], pkg[1])

# google-genai imports
info = {'ok': False, 'version': None, 'error': None}
try:
    import google.genai as genai
    info['ok'] = True
    ver = getattr(genai, '__version__', None) or getattr(genai, 'version', None)
    if ver is None:
        try:
            import pkg_resources
            ver = pkg_resources.get_distribution('google-genai').version
        except Exception:
            ver = None
    info['version'] = ver
    # check types import
    try:
        from google.genai import types
        info['types_import_ok'] = True
    except Exception as e:
        info['types_import_ok'] = False
        info['types_error'] = str(e)
except Exception as e:
    info['error'] = str(e)
checks['google-genai'] = info

print(json.dumps(checks, indent=2))
