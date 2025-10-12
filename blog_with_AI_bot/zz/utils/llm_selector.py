#zz/llm_selector.py
import time, logging

from blg.llm_clients import get_llm_client

logger = logging.getLogger(__name__)


def generate_via_selector(prompt: str, source: str | None = None) -> str:
    """
    Unified entrypoint for all text generation requests.
    Uses get_llm_client() to choose provider.
    """
    start = time.perf_counter()

    client = get_llm_client(source)
    result = client.generate(prompt)

    elapsed = time.perf_counter() - start
    logger.info(
        f"[GEN] source={source or 'default'} | model={getattr(client, 'model_name', getattr(client, 'model', 'unknown'))} | "
        f"time={elapsed:.2f}s | prompt={prompt[:60].replace('\n',' ')}..."
    )

    return result 