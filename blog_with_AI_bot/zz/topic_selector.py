# zz/services/topic_selector.py
from __future__ import annotations
from typing import Iterable

# Простейшие пороги — можно вынести в settings
DEFAULT_MIN_SCORE = 50
DEFAULT_MIN_COMMENTS = 10


def accept_topic(score: int, comments: int, *, min_score: int = DEFAULT_MIN_SCORE, min_comments: int = DEFAULT_MIN_COMMENTS) -> bool:
    """Вернуть True если тема достаточно «горячая» по метрикам."""
    return score >= min_score and comments >= min_comments