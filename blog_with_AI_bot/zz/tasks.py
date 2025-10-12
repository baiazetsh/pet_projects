#zz/tasks.py
from __future__ import annotations
from celery import shared_task
from zz.models import Post, Chapter, Comment
from django.contrib.auth import get_user_model
from django.conf import settings
from zz.utils.metrics import track_bot_reply, track_summarize_time
import re
import time
import random
import logging
from zz.utils.bots import ensure_bot_user
from zz.utils.ollama_client import (
    generate_text, 
    clean_response, 
    list_models, 
    check_model_availability, 
    get_ollama_client
)
from django.shortcuts import get_object_or_404
from zz.utils.utils import notify_new_comment  
from zz.utils.llm_selector import generate_via_selector
from zz.utils.source_selector import get_active_source
from typing import List
from zz.parsers.hackernews import HackerNewsParser
#from zz.parsers.reddit import RedditParser
#from zz.parsers.twitter import TwitterParser
#from zz.parsers.vc_ru import VcRuParser
#from zz.parsers.pikabu import PikabuParser

from zz.topic_cleaner import normalize_title, make_hash_key
from zz.topic_selector import accept_topic
from zz.models import ParsedTopic, GeneratedChain
from zz.topic_generator import generate_for_topic

logger = logging.getLogger(__name__)
source = get_active_source()

# ⚙️ Параметры можно вынести в settings.py
ENABLED_SOURCES = getattr(settings, "TOPIC_SOURCES", ["hackernews"])  # позже расширим
MIN_SCORE = getattr(settings, "TOPIC_MIN_SCORE", 50)
MIN_COMMENTS = getattr(settings, "TOPIC_MIN_COMMENTS", 10)
FETCH_LIMIT = getattr(settings, "TOPIC_FETCH_LIMIT", 50)


@shared_task
def fetch_trending_topics() -> int:
    """Собрать горячие темы из включённых источников и сохранить в БД."""
    # 1) Подбираем парсеры
    parsers = []
    if "hackernews" in ENABLED_SOURCES:
        parsers.append(HackerNewsParser())
    """
    if "reddit" in ENABLED_SOURCES:
        parsers.append(RedditParser())
    if "twitter" in ENABLED_SOURCES:
        parsers.append(TwitterParser())
    if "vc_ru" in ENABLED_SOURCES:
        parsers.append(VcRuParser())
    if "pikabu" in ENABLED_SOURCES:
        parsers.append(PikabuParser())
    """

    created = 0

    for parser in parsers:
        try:
            items = parser.fetch(limit=FETCH_LIMIT)
        except Exception:
            continue

        for it in items:
            if not accept_topic(it["score"], it["comments"], min_score=MIN_SCORE, min_comments=MIN_COMMENTS):
                continue

            title_clean = normalize_title(it["title"]) or it["title"][:120]
            hk = make_hash_key(it["source"], title_clean)

            # dedup: не создаём дубль
            if ParsedTopic.objects.filter(hash_key=hk).exists():
                continue

            ParsedTopic.objects.create(
                source=it["source"],
                title_raw=it["title"],
                title_clean=title_clean,
                url=it.get("url", ""),
                score=it.get("score", 0),
                comments=it.get("comments", 0),
                hash_key=hk,
            )
            created += 1

    return created




SOURCE_SWITCH = getattr(settings, "TOPIC_GENERATION_SOURCE", "local")  # 'local'|'ollama'|'grok'
BATCH_SIZE = getattr(settings, "TOPIC_GENERATION_BATCH", 10)


@shared_task
def generate_chains_for_new_topics() -> int:
    """
    Take unprocessed topics → generate content chain → save to GeneratedChain.
    Returns count of successful generations.
    """
    qs = ParsedTopic.objects.filter(processed=False).order_by("-created_at")[:BATCH_SIZE]
    total = 0

    for topic in qs:
        raw, model_name = generate_for_topic(topic.title_clean or topic.title_raw, source_switch=SOURCE_SWITCH)
        status = "ok"
        err = ""
        if raw.startswith("[generation error]"):
            status = "error"
            err = raw

        GeneratedChain.objects.create(
            topic=topic,
            model=model_name,
            source_switch=SOURCE_SWITCH,
            prompt_snapshot=(topic.title_clean or topic.title_raw),
            raw_output=raw,
            status=status,
            error_message=err,
        )

        topic.processed = True
        topic.save(update_fields=["processed"])
        total += 1

    return total


@shared_task(bind=True, max_retries=3)
def summarize_post(self, post_id: int) -> str:
    """
    Async task: to make short summary of post with Ollama
    """
    start = time.time()

    try:
        post = get_object_or_404(Post, pk=post_id)

        prompt =(
            f"Сделай краткое резюме текста (3–4 предложения, без воды, по сути):\n\n"
            f"{post.content[:1500]}"            
        )
        # Text generation with Ollama
        """
        raw_text = generate_text(
            prompt=prompt,
            model=settings.LLM_MODEL
        )
        """
        raw_text = generate_via_selector(prompt, source=source)

        summary = clean_response(raw_text).strip()

        if not summary:
            summary = "🤷 The model was unable to generate a resume. "

        #save into DB
        post.summary = summary
        post.save(update_fields=["summary"])

        logger.info(f"[SUMMARY] Post {post.id}: {summary[:60]}...")

        track_summarize_time(time.time() - start)
        return summary

    except Exception as e:
        logger.error(f"[SUMMARY ERROR] post_id={post_id}: {e}")
        raise self.retry(exc=e, countdown=5)



@shared_task
def generate_post(chapter_id, title):
    """
    Фоновая задача: создаёт пост в базе данных.
    В реальном проекте здесь может быть вызов Ollama API.
    """
    start = time.time()

    chapter = Chapter.objects.get(id=chapter_id)
    body = f"Сгенерированный текст для: {title}"
    post = Post.objects.create(
        chapter=chapter,
        title=title,
        content=body,
        )
    
    track_summarize_time(time.time() - start)
    return {"post_id": post.id, "title": title}

# отдельная Celery задача для генерации ответов ботов
@shared_task
def generate_bot_reply_task(comment_id, bot_profile):
    """Celery задача для генерации ответа бота"""
    start = time.time()

    try:
        instance = Comment.objects.get(id=comment_id)
        username = bot_profile["username"]
        bot_user = ensure_bot_user(bot_profile)
        
        # Проверка наличия настройки модели
        if not hasattr(settings, 'LLM_MODEL') or not settings.LLM_MODEL:
            logger.error(f"[{username}] LLM_MODEL не настроен в settings")
            return {"error": "LLM_MODEL not configured"}
        
        # История последних 5 комментов
        recent_comments = Comment.objects.filter(post=instance.post).order_by("-created_at")[:5]
        dialogue = "\n".join(
            f"{c.author.username}:{c.content.replace('\n', ' ')[:500]}"
            for c in reversed(recent_comments))
        dialogue = dialogue[:2000]
        
        logger.info(f"[{username}] Готовлю ответ на коммент id={instance.id}")
        
        # Запрос к модели
        try:
            client = get_ollama_client()
            response = client.chat(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": bot_profile["style"]},
                    {"role": "user", "content": f"Вот обсуждение:\n{dialogue}\n\nДай ответ на последний коммент."}
                ],
                stream=False
            )
        except Exception as ollama_error:
            logger.error(f"[{username}] Ошибка Ollama: {ollama_error}")
            reply_text = "🤷 Модель временно недоступна."
        else:
            reply_text = clean_response(
                (response or {}).get("message", {}).get("content", "").strip()
                )
            
            if not reply_text or len(reply_text) < 3:
                reply_text = "🤷 Нечего сказать."

        # имитация "подумал перед ответом"
        #time.sleep(random.randint(2, 6))
                
        comment = Comment.objects.create(
            post=instance.post,
            author=bot_user,
            content=reply_text,
            bot_replied=True
        )
        # set a flag that there was a response to instance
        instance.bot_replied = True
        instance.save(update_fields=["bot_replied"])

        logger.info(
            f"[{username}] ответил: {reply_text[:60]}... coment_id:{comment_id} post_id:{instance.post_id}"
            )
        
        notify_new_comment(comment)
        
        track_summarize_time(time.time() - start)

        return {
            "success": True,
            "comment_id": comment.id,
            "bot": username,
            "reply": reply_text[:60]
        }

    except Comment.DoesNotExist:
        logger.error(f"Comment with id={comment_id} not found")
        return {"error": f"Comment {comment_id} not found"}
    except Exception as e:
        logger.error(f"[{bot_profile.get('username', 'BOT')} ERROR] {e}")
        return {"error": str(e)}

