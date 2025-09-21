# utils/ollama_client.py
import re
import requests
from django.conf import settings
import logging
from ollama import Client

logger = logging.getLogger(__name__)

#----------base func-----------

def get_ollama_client():
    """Returns Ollama client with URL from settings"""
    url = getattr(settings, "OLLAMA_URL", "http://ollama:11434")
    return Client(host=url)
    

def generate_text(prompt: str, model: str = None) -> str:
    """Отправить запрос в Ollama для генерации текста"""
    try:
        if model is None:
            model = getattr(settings, 'OLLAMA_MODEL', None)
        if not model:
            raise ValueError("Модель не указана и OLLAMA_MODEL не настроен")

        url = getattr(settings, "OLLAMA_URL", "http://ollama:11434") + "/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()

        data = resp.json()        
        return data.get("response", "")

    except Exception as e:
        logger.error(f"[OLLAMA_ERROR] generate_text failed: {e}")
        raise


def list_models() -> list[str]:
    """Returns a list of available Ollama model"""
    try:
        url = getattr(settings, "OLLAMA_URL", "http://ollama:11434") + "/api/tags"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        data = resp.json()
        models = [m["name"] for m in data.get("models", [])]
        return models

    except Exception as e:
        logger.error(f"[OLLAMA ERROR] list_models failed: {e}")
        return []


def clean_response(text: str) -> str:
    """Removes the service reflections (<think>...</think>)."""
    if not text:
        return ""
    # убираем размышления <think> убираем markdown-разметку (*, #, _)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"[*#_`]+", "", cleaned)

    return cleaned.strip()


        
def check_model_availability() -> tuple[bool, list[str]]:
    """Checks if a model is available in Ollama"""
    """Returns (is_available, list_of_models)"""
    try:         
        available_models = list_models()
        
        if not hasattr(settings, 'OLLAMA_MODEL'):
            logger.error("❌ OLLAMA_MODEL didn't setted in settings.py")
            return False, available_models
        
        model_name = settings.OLLAMA_MODEL
        if model_name not in available_models:
            logger.error(f"❌ Model {model_name} not found. Available models: {available_models}")
            return False, available_models
        
        return True, available_models

    except Exception as e:
        logger.error(f"❌ Error connecting to Ollama: {e}")
        return False, []    



