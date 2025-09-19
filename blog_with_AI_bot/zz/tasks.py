#tasks.py
from celery import shared_task
from zz.models import Post, Chapter, Comment
from ollama import Client
from django.contrib.auth import get_user_model
from django.conf import settings
import re
import time
import random
import logging

logger = logging.getLogger(__name__)

def clean_response(text: str) -> str:
    """Удаляет служебные размышления (<think>...</think>)."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def ensure_bot_user(bot_profile):
    """Создаёт или получает пользователя-бота"""
    User = get_user_model()
    from django.db.utils import IntegrityError
    try:
        bot_user, _  = User.objects.get_or_create(
            username=bot_profile["username"],
            defaults={
                'email': f"{bot_profile['username'].lower()}@site.com",
                'is_active':True,
            }
        )
        return bot_user
    except IntegrityError:
        return User.objects.get(username=bot_profile["username"])

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
        recent_comments = Comment.objects.filter(post=instance.post).order_by("created_at")[:5]
        dialogue = "\n".join(f"{c.author.username}:{c.content}" for c in reversed(recent_comments))
        
        logger.info(f"[{username}] Готовлю ответ на коммент id={instance.id}")
        
        # Запрос к модели
        try:
            client = Client()
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
            reply_text = clean_response(response["message"]["content"].strip())
            if not reply_text or len(reply_text) < 3:
                reply_text = "🤷 Нечего сказать."

        # имитация "подумал перед ответом"
        time.sleep(random.randint(2, 6))
                
        comment = Comment.objects.create(
            post=instance.post,
            author=bot_user,
            content=reply_text
        )

        logger.info(f"[{username}] ответил: {reply_text[:60]}...")
        
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
    