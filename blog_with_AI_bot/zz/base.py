# zz/parsers/base.py
from __future__ import annotations
from typing import TypedDict, List

class TopicDict(TypedDict):
    # Унифицированный формат темы, которую вернёт любой парсер
    source: str
    title: str
    url: str
    score: int
    comments: int

class BaseParser:
    """Базовый интерфейс для всех парсеров."""

    source_name: str = "base"

    def fetch(self, limit: int = 50) -> List[TopicDict]:
        raise NotImplementedError