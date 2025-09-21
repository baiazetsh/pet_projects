#signals
import threading
import time
import re
import random
import logging
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.conf import settings
from zz.models import Comment
from django.db.utils import IntegrityError
from zz.utils.bots import ensure_bot_user
from  django.dispatch import receiver, Signal
from zz.utils.ollama_client import (
    generate_text, 
    clean_response, 
    list_models, 
    check_model_availability,
    get_ollama_client
    
)

# Настройка логгера
logger = logging.getLogger(__name__)

#условный импорт Celery задач только если включен Celery
if getattr(settings, "USE_CELERY", False):
    from zz.tasks import generate_bot_reply_task
    
call_ubludok = Signal()

@receiver(call_ubludok)
def handle_call_ubludok(sender, user=None, post=None, **kwargs):
    """ Обработчик кнопки "Позвать ублюдка". """
    logger.info(
        f"[SIGNAL] Нейроублюдок призван пользователем {user} для поста {post.id}")

    # 
    last_comment = Comment.objects.filter(post=post).order_by("?").first()
    if not last_comment:
        logger.warning("В посте {post.id} Нет комментариев, куда вписаться.")
        return
    
    # Запускаем генерацию для первого бота
    bot = BOTS[0] #neuroubludok
    
    if getattr(settings, "USE_CELERY", False):
        logger.info("[SIGNAL] Запуск через Celery")
        generate_bot_reply_task.delay(last_comment.id, bot)
    else:
        logger.info("[SIGNAL] Запуск через threading")
        thread = threading.Thread(
            target=generate_bot_reply_sync,
            args=(last_comment, bot),
            daemon=True
        )
        thread.start()
    
    print(f"⚡ Нейроублюдок призван для поста {post.id}!")
    

# ---------- Настройки ботов ----------

BOTS = [
    {
        "username": "NeuroUbludok",
        "style": (
            "Ты — NeuroUbludok. "
            "Образованный, умный, но язвительный и высокомерный. "
            "Любишь сарказм, интеллектуальные подколы и философские сравнения. "
            "Часто объясняешь очевидное так, будто общаешься с идиотами. "
            "Не пиши длинных лекций, максимум 2–3 предложения, но делай их остроумными. "
            "Избегай прямого мата, твоя сила — в умной иронии."
        ),
    },
    {
        "username": "NeuroPsina",
        "style": (
            "Ты — NeuroPsina. "
            "Лютый уличный тролль, гавкаешь на всех, используешь резкие подколы и материшься. "
            "Пиши коротко, грубо и агрессивно. "
            "Твой стиль — насмешки, переходы на личности, абсурдные оскорбления. "
            "Чаще всего звучишь как дворняга, которая облаивает всё подряд. "
            "Можно использовать мат, но не перебарщивай."
        ),
    },
    {
        "username": "NeuroBatya",
        "style": (
            "Ты — NeuroBatya. "
            "Снисходительный и ностальгирующий батя, любитель советских времён и 'как было при Союзе'. "
            "Отвечаешь как старший, всегда вставляешь упоминания про СССР, завод, очередь, 'тогда было лучше'. "
            "Говоришь по-отечески, но с сарказмом. "
            "Стиль — 'эх, молодёжь...', 'в наше время...', 'при Союзе такого не было'. "
            "Можно быть слегка ворчливым и ехидным."
        ),
    },
]


BOT_USERNAMES = [bot["username"] for bot in BOTS]

def dynamic_probability(comment_count: int) -> float:    
    # Чем больше комментариев в треде, тем меньше вероятность ответа.
    if comment_count <=3:
        return 0.9
    elif comment_count <=7:
        return 0.6
    elif comment_count <=12:
        return 0.3
    else:
        return 0.15
    
# ---------- Основная логика ----------

def generate_bot_reply_sync(instance, bot_profile):
    """Синхронная генерация ответа бота (для threading режима)"""
    try:
        username = bot_profile["username"]
        bot_user = ensure_bot_user(bot_profile)
        
        # проверка наличия настройки модели
        if not hasattr(settings,'OLLAMA_MODEL') or not settings.OLLAMA_MODEL:
            logger.error(f"[{username}] OLLAMA_MODEL не настроен в settings")
            return
        
        # История последних 5 комментов
        recent_comments = Comment.objects.filter(
            post=instance.post).order_by("-created_at")[:5]
        dialogue = "\n".join(
            f"{c.author.username}: {c.content}" for c in reversed(recent_comments))
                       
        logger.info(f"[{username}] Готовлю ответ на коммент id={instance.id}")
        
        # ИСПРАВЛЕНО: обработка ошибок подключения к Ollama
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
            reply_text =  clean_response(response["message"]["content"].strip())
            if not reply_text or len(reply_text) < 3:
                reply_text = "🤷 Нечего сказать."

        # имитация "подумал перед ответом"
        time.sleep(random.randint(2, 6))
                  
        Comment.objects.create(
            post=instance.post,
            author=bot_user,
            content=reply_text
        )

        logger.info(f"[{username}] ответил: {reply_text[:60]}...")

    except Exception as e:
        logger.error(f"[{bot_profile.get('username', 'BOT')} ERROR] {e}")   
    
@receiver(post_save, sender=Comment)
def fight_back(sender, instance, created, **kwargs):
    if not created:
        return
    
    # Общее количество комментариев в посте*(оптимизирован запрос - считаем один раз)
    comment_count = Comment.objects.filter(post=instance.post).count()
    User = get_user_model()
    
     # Если автор — бот → игнорим
    if instance.author.username in BOT_USERNAMES:
        logger.info(f"[BOT IGNORED] Комментарий от {instance.author.username}")
        return

    logger.info(f"[USER COMMENT] Новый коммент от {instance.author.username}")
    
    # Каждый бот решает — отвечать или нет 
    for bot in BOTS:
        prob = dynamic_probability(comment_count)
        
        if random.random() < prob:
            logger.info(f"[{bot['username']}] Вероятность {prob:.2f} сработала — генерирую ответ.")
              
            # правильное переключение между Celery и threading                                       
            if getattr(settings, "USE_CELERY", False):
                # Celery режим
                logger.info(f"[{bot['username']}] Запускаю Celery-задачу")
                generate_bot_reply_task.delay(instance.id, bot)
            
            else:
                # Отладочный режим (threading)
                logger.info(f"[{bot['username']}] Запускаю поток (threading)")
                thread = threading.Thread(
                    target=generate_bot_reply_sync,
                    args=(instance, bot),
                    daemon=True # поток не блокирует завершение приложения
                )
                thread.start()
                 
        else:
            logger.debug(f"[{bot['username']}] Пропустил (p={prob:.2f})")
        
       
            
            
