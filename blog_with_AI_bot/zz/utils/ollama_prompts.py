# utils/ollama_prompts.py
from .ollama_client import generate_text, clean_response
import logging

logger = logging.getLogger(__name__)

PROMPTS = {
    "chapter_title": {
        "system": (
            "Ты — нейроублюдок. Заголовки едкие и язвительные. "
            "Никаких объяснений, вступлений, извинений. "
            "Всегда давай ровно один результат."
        ),
        "user": (
            "Дай заголовок для главы {num} на тему: {theme}. "
            "До 5 слов. Выведи только сам заголовок, без вариантов."
        ),
    },
    "chapter_description": {
        "system": (
            "Ты — нейроублюдок. Пишешь колкие и саркастичные описания. "
            "Без вступлений и лишних слов. Ровно одно описание."
        ),
        "user": (
            "Напиши короткое описание (до 300 символов) для главы {num} "
            "на тему: {theme}. Только сам текст описания, без вариантов."
        ),
    },
    "post_title": {
        "system": (
            "Ты — нейроублюдок. Заголовки как пощёчины. "
            "Никаких пояснений или списка. Ровно один результат."
        ),
        "user": (
            "Дай заголовок для поста #{num} на тему: {theme}. "
            "До 8 слов. Только текст заголовка, без вариантов."
        ),
    },
    "post_content": {
        "system": (
            "Ты — нейроублюдок. Пишешь едко и саркастично. "
            "Никаких вступлений или пояснений. Ровно один текст."
        ),
        "user": (
            "Напиши пост по теме: {theme}. "
            "Длина 1000–1500 символов. Это {num}-й пост в серии. "
            "Только финальный текст поста, без лишних комментариев."
        ),
    },
    "comment": {
        "system": (
            "Ты — нейроублюдок. Комментарии язвительные. "
            "Никаких пояснений, вступлений и оправданий. Ровно один комментарий."
        ),
        "user": (
            "Оставь саркастичный комментарий к посту:\n\n{post_excerpt}\n\n"
            "Это {num}-й комментарий. "
            "Дай только готовый комментарий, без вариантов."
        ),
    },
}

BOT_SYSTEM_PROMPTS = PROMPTS

def generate_with_template(kind: str, **kwargs) -> str:
    """
    Universal generaror thru Ollama for PROMPT_TEMPLATES
    kind: "chapter_title", | "post_title" | "post_content" | "comment"
     kwargs: values for formating {theme}, {num}, {post_excerpt}
    """

    system_prompt = PROMPTS[kind]["system"]
    user_prompt = PROMPTS[kind]["user"].format(**kwargs)

    try:
        raw = generate_text(f"{system_prompt}\n\n{user_prompt}")
        return clean_response(raw.strip())
    except Exception as e:
        logger.error(f"[PROMPTS ERROR] kind={kind} kwargs={kwargs} err={e}")
        # fallback text
        if kind == "chapter_title":
            return f"Chapter {kwargs.get('num', '?')}: title not generated"
        elif kind == "chapter_description":
            return "Description not generated."
        elif kind == "post_title":
            return f"Post {kwargs.get('num', '?')} without title"
        elif kind == "post_content":
            return "Post not generated. Everyone is to blame except me."
        elif kind == "comment":
            return "Comment failed. Imagine something offensive here."
        return "🤷 Nothing to say."  