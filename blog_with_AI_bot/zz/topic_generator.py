#zz/services/topic_generator.py
from __future__ import annotations
from typing import Optional, Tuple
from django.conf import settings

# Интеграция с существующей функцией project: generate_via_selector
# Если её нет — fallback на прямой вызов клиента из blg.llm_clients

def generate_for_topic(thesis: str, source_switch: Optional[str] = None) -> Tuple[str, str]:
    """Сгенерировать цепочку по теме.
    Возвращает (raw_output, model_used).
    """
    prompt = (
        "Topic: " + thesis + "\n\n"
        "Generate a discussion chain:\n"
        "1) Chapter (1 title)\n2) Post (short)\n3) 3 comments (concise).\n"
    )

    model_name = ""

    # 1) Пробуем общий селектор
    try:
        from zz.llm_selector import generate_via_selector  # type: ignore
        raw = generate_via_selector(prompt, source=source_switch or "local")
        model_name = getattr(settings, "GROK_NAME_MODEL", "") if (source_switch == "grok") else getattr(settings, "LLM_MODEL", "")
        return raw, model_name
    except Exception:
        pass
    # 2) Fallback: прямой клиент
    try:
        from blg.llm_clients import get_llm_client  # type: ignore
        client = get_llm_client(source_switch or "local")
        raw = client.generate(prompt)
        model_name = getattr(settings, "LLM_MODEL", "")
        return raw, model_name
    except Exception as e:
        return f"[generation error] {e}", model_name