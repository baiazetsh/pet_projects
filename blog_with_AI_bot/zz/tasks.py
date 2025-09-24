#tasks.py
from celery import shared_task
from zz.models import Post, Chapter, Comment
from django.contrib.auth import get_user_model
from django.conf import settings
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



logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def summarize_post(self, post_id: int) -> str:
    """
    Async task: to make short summary of post with Ollama
    """
    try:
        post = get_object_or_404(Post, pk=post_id)

        prompt =(
            f"Сделай краткое резюме текста (3–4 предложения, без воды, по сути):\n\n"
            f"{post.content[:1500]}"            
        )
        # Text generation with Ollama
        raw_text = generate_text(
            prompt=prompt,
            model=settings.OLLAMA_MODEL
        )

        summary = clean_response(raw_text).strip()

        if not summary:
            summary = "🤷 The model was unable to generate a resume. "

        #save into DB
        post.summary = summary
        post.save(update_fields=["summary"])

        logger.info(f"[SUMMARY] Post {post.id}: {summary[:60]}...")
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
    chapter = Chapter.objects.get(id=chapter_id)
    body = f"Сгенерированный текст для: {title}"
    post = Post.objects.create(
        chapter=chapter,
        title=title,
        content=body,
        )
    return {"post_id": post.id, "title": title}

# отдельная Celery задача для генерации ответов ботов
@shared_task
def generate_bot_reply_task(comment_id, bot_profile):
    """Celery задача для генерации ответа бота"""
    try:
        instance = Comment.objects.get(id=comment_id)
        username = bot_profile["username"]
        bot_user = ensure_bot_user(bot_profile)
        
        # Проверка наличия настройки модели
        if not hasattr(settings, 'OLLAMA_MODEL') or not settings.OLLAMA_MODEL:
            logger.error(f"[{username}] OLLAMA_MODEL не настроен в settings")
            return {"error": "OLLAMA_MODEL not configured"}
        
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
                model=settings.OLLAMA_MODEL,
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

