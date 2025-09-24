# utils/ollama_prompts.py
from .ollama_client import generate_text, clean_response
import logging

logger = logging.getLogger(__name__)

PROMPTS = {
    "chapter_title": {
        "system": "Ты — нейроублюдок. Придумываешь заголовки с издёвкой.",
        "user": "Придумай язвительное, саркастичное название для главы {num} на тему: {theme}. Максимум 5 слов."
    },
    "post_title": {
        "system": "Ты — нейроублюдок. Заголовки — как пощёчины.",
        "user": "Придумай провокационный заголовок для поста #{num} на тему: {theme}. Максимум 8 слов."
    },
    "post_content": {
        "system": "Ты — нейроублюдок. Пишешь посты с едким сарказмом, как кислота на нервы.",
        "user": "Напиши пост длиной 1000–1500 символов по теме: {theme}. "
                "Будь максимально язвительным, саркастичным, провокационным. Без разметки. "
                "Это {num}-й пост в серии."
    },
    "comment": {
        "system": "Ты — нейроублюдок. Твои комменты — как нож в спину, но с улыбкой.",
        "user": "Оставь язвительный, саркастичный комментарий к этому посту:\n\n{post_excerpt}\n\n"
                "Не повторяй пост. Будь оригинален. Это {num}-й комментарий."
    }
}

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
        elif kind == "post_title":
            return f"Post {kwargs.get('num', '?')} without title"
        elif kind == "post_content":
            return "Post not generated. Everyone is to blame except me."
        elif kind == "comment":
            return "Comment failed. Imagine something offensive here."
        return "🤷 Nothing to say."  