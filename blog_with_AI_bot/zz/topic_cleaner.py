# zz/topic_cleaner.py
from __future__ import annotations
import re

# Простая нормализация заголовков под промпт-модель
# – удалить URL, эмодзи, лишние пробелы; урезать длину и привести к красивому виду

EMOJI_RE = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
URL_RE = re.compile(r"https?://\S+", flags=re.IGNORECASE)
SPACES_RE = re.compile(r"\s+")

MAX_WORDS = 12


def normalize_title(title: str) -> str:
    """Очистить и ужать до тезиса для передачи в LLM-промпт."""
    t = URL_RE.sub("", title)
    t = EMOJI_RE.sub("", t)
    t = t.strip()
    t = SPACES_RE.sub(" ", t)
    words = t.split()
    if len(words) > MAX_WORDS:
        t = " ".join(words[:MAX_WORDS])
    # Первая буква — заглавная, остальное как есть
    if t:
        t = t[0].upper() + t[1:]
    return t


def make_hash_key(source: str, title: str) -> str:
    """Хеш-ключ для дедупликации (упростим до sha1).
    В реале — добавить нормализацию и домен URL.
    """
    import hashlib
    base = f"{source}|{title}".encode("utf-8", errors="ignore")
    return hashlib.sha1(base).hexdigest()