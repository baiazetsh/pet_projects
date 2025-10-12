#blg/llm_clients.py
"""
LLM Clients Router
Stage 1: basic routing between Ollama, local Mini Server< and Grok(stub only)
"""

from  __future__ import annotations
import time, json, logging
from typing import Protocol, Any
import requests

from django.conf import settings

logger = logging.getLogger(__name__)



#-----------Base interface-------------
class BaseLLMClient(Protocol):
    """Base interface for all LLM clients."""

    def generate(self, prompt: str, **kwargs: Any) -> str:
        ...


# --------------Ollama Client---------
class OllamaClient:
    """
    Working client that sends prompts to a local Ollama instance.
    For now, it assumes your Gemma model is running on localhost:11434.
    """

    def __init__(self,
                model_name: str = settings.LLM_MODEL,
                base_url: str = settings.LLM_URL
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Send a prompt to the local Ollama model and return generated text."""
        logger.debug(f"OllamaCient.generate() called with model={self.model_name}")

        start = time.perf_counter()

        payload = {"model": self.model_name, "prompt": prompt, "stream": False}
        url = f"{self.base_url}/api/generate"

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()

            #  Сначала попробуем обычный JSON (нестрим)
            try:
                data = response.json()
                result = data.get("response", "")
            except Exception:                
            #  Фолбэк: сервер выдал стрим — склеим по строкам
                text_parts = []
                for line in response.text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if "response" in obj:
                            text_parts.append(obj["response"])
                    except Exception:
                        # не JSON — игнорим
                        continue
                #  Если ничего не собрали — вернём сырой текст (крайний случай)
                result = "".join(text_parts) if text_parts else response.text

        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            result =  f"[Ollama error]: {e}"

        finally:
            elapsed = time.perf_counter() - start
            logger.info(
                f"[GEN] source=ollama | model={self.model_name} | time={elapsed:.2f}s | "
                f"prompt={prompt[:60].replace('\n',' ')}..."
            )

        return result

            

#------Stub Client--------------
class StubClient:
    """
    Placeholder for not-yet-implemented providers(Local Mini Server< Grok).
    Return static text for testing pipelines integrity.
    """

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    def generate(self, prompt: str, **kwargs: Any) -> str:
        logger.debug(f"StubClient called for providers={self.provider_name}")
        return f"[Stub: {self.provider_name}] Pipeline OK. Prompt was: {prompt[:60]}..."


class GrokClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.GROK_API_KEY
        self.model = model or settings.GROK_NAME_MODEL
        self.url = settings.GROK_URL

    def generate(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": 0.7
        }
        r = requests.post(self.url, headers=headers, json=data, timeout=60)
        print("🛰️ STATUS:", r.status_code, r.text[:200])  # debug
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]



class MiniServerClient:
    """
    Client for local Mini Server(Qwen3:8b)
    """
    def __init__(self,
                 model_name: str = "qwen3:8b", base_url: str | None = None):
        self.model_name = model_name
        self.base_url = (base_url or settings.MINI_SERVER_URL).rstrip("/")
        
    def generate(self, prompt: str, **kwargs: Any) -> str:
        start = time.perf_counter()
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        url = f"{self.base_url}/api/generate"
        
        try:
            r = requests.post(url, json=payload, timeout=120)
            r.raise_for_status()
            try:
                data = r.json()
                result = data.get("response", "")
            except Exception:
                #fallback, if response is stream
                text_parts = []
                for line in r.text.splitlines():
                    try:
                        obj = json.loads(line)
                        if "response" in obj:
                            text_parts.append(obj["response"])                        
                    except Exception:
                        continue
                result = "".join(text_parts) if text_parts else r.text
        except Exception as e:
            logger.error(f"MiniServer request failed: {e}")
            result = f"[MiniServer error]: {e}"
        
        elapsed = time.perf_counter() - start
        logger.info(
            f"[GEN] source=mini_server| model={self.model_name} | time={elapsed:.2f}s")
        return result
        
        

#--------Router function-------
def get_llm_client(source: str | None = None) -> BaseLLMClient:
    """
    Returns the appropriate LLM clioent instance based on the source value.
    Currently supports:
     - 'ollama' → OllamaClient (Gemma)
     - 'local'  → StubClient for local mini server
     - 'grok'   → StubClient for Grok API
    """

    if not source:
        source = "ollama"

    source = source.lower()    

    if source == "ollama":
        logger.info("Using Ollama client (Genna model)")
        return OllamaClient()

    elif  source == "local":
        logger.info("Using  Mini Server client (Qwen3:8)")
        return MiniServerClient()

    elif source == "grok":
        logger.info("Using Grok client (via API)")
        return GrokClient()

    else:
        logger.warning(f"Unknown LLM source'{source}, defaulting to Ollama")
        return OllamaClient()



