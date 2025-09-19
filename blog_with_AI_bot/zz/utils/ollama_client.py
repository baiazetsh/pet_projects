# utils/ollama_client.py
import requests
from django.conf import settings

BASE_URL = settings.OLLAMA_URL
DEFAULT_MODEL = settings.OLLAMA_MODEL

def list_models():
    """Получить список доступных моделей из Ollama"""
    url = f"{BASE_URL}/api/tags"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return [m["name"] for m in data.get("models", [])]

def generate_text(prompt: str, model: str = None) -> str:
    """Отправить запрос в Ollama для генерации текста"""
    if model is None:
        model = DEFAULT_MODEL
        
    url = f"{BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  # stream=False → ответ вернётся одним куском
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "")
