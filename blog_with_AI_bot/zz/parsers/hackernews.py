# zz/parsers/hackernews.py
from __future__ import annotations
from typing import List
import json, time
import urllib.request
from zz.base import BaseParser, TopicDict

# ⚠️ Без внешних библиотек: используем встроенный urllib для доступа к HN API
# Документация: https://github.com/HackerNews/API

class HackerNewsParser(BaseParser):
    source_name = "hackernews"

    def _get(self, url: str) -> dict:
        # Простейший GET с retry — HN API быстрый и стабильный
        for _ in range(3):
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = resp.read().decode("utf-8")
                return json.loads(data)
            time.sleep(0.3)
        return {}

    def fetch(self, limit: int = 50) -> List[TopicDict]:
        base = "https://hacker-news.firebaseio.com/v0"
        ids = self._get(f"{base}/topstories.json")[:limit]
        out: List[TopicDict] = []
        for sid in ids:
            item = self._get(f"{base}/item/{sid}.json")
            if not item or item.get("type") != "story":
                continue
            title = item.get("title") or ""
            url = item.get("url") or f"https://news.ycombinator.com/item?id={sid}"
            score = int(item.get("score") or 0)
            comments = int(item.get("descendants") or 0)
            out.append(TopicDict(
                source=self.source_name,
                title=title,
                url=url,
                score=score,
                comments=comments,
            ))
        return out