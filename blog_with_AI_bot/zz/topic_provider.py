# zz/topic_provider.py

from __future__ import annotations
from encodings import normalize_encoding
from typing import Optional
from zz.parsers.hackernews import HackerNewsParser
from zz.topic_cleaner import normalize_title
from zz.topic_selector import accept_topic

def get_ready_topic() -> Optional[str]:
    """
    Fetch and prepare one trending< cleaning topic title for generation
    """
    
    parser = HackerNewsParser()
    topics = parser.fetch(limit=30)
    
    for t in topics:
        score = t.get("score", 0)
        comments = t.get("comments", 0)
        title = t.get("title", "")
        if accept_topic(score, comments):
            normalized = normalize_title(title)
            if normalized:
                return normalized
    return None            