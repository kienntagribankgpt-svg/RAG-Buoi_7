import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
        self.provider = os.getenv("LLM_PROVIDER", "ollama")

    def check_health(self) -> dict:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                models = [m.get("name") for m in resp.json().get("models", [])]
                return {"online": True, "models": models, "url": self.base_url}
        except Exception:
            pass
        return {"online": False, "models": [], "url": self.base_url}

    def generate(self, prompt: str, format_json: bool = False, temperature: float = 0.2) -> str:
        health = self.check_health()
        if not health["online"]:
            return "OLLAMA_OFFLINE_FALLBACK"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }
        if format_json:
            payload["format"] = "json"
        try:
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=180)
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            return f"OLLAMA_ERROR: {str(e)}"
        return "OLLAMA_OFFLINE_FALLBACK"

if __name__ == "__main__":
    client = OllamaClient()
    h = client.check_health()
    print(f"OLLAMA ADAPTER: PASS")
    print(f"OLLAMA SERVER ONLINE: {'YES' if h['online'] else 'NO'} ({h['url']})")
