#signals
import time
import threading
import random
import logging
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from django.conf import settings

from zz.models import Comment, Post
from zz.utils.bots import ensure_bot_user, BOTS, BOT_USERNAMES
from  django.dispatch import receiver, Signal
from zz.utils.ollama_client import (
    generate_text, 
    clean_response, 
    list_models, 
    check_model_availability,
    get_ollama_client
    
)
from zz.utils import notify_new_comment
from zz.utils.task_runner import run_task


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
    last_comment = Comment.objects.filter(post=post).order_by("-created_at").first()
    if not last_comment:
        logger.warning(f"В посте {post.id} Нет комментариев, куда вписаться.")
        return
    
    # Запускаем генерацию для первого бота
    bot = BOTS[0] #neuroubludok
    run_task(generate_bot_reply_sync, last_comment.id, bot, use_celery_name="generate_bot_reply_task")        
    logger.info(f"[SIGNAL] Ублюдок пошёл генерировать ответ для поста {post.id}")    

# ---------- Настройки ботов ----------

def dynamic_probability(comment_count: int) -> float:    
    # Чем больше комментариев в треде, тем меньше вероятность ответа.
    if comment_count <=3:
        return 0.9
    elif comment_count <=7:
        return 0.7
    elif comment_count <=12:
        return 0.8
    else:
        return 0.9
    
# ---------- Основная логика ----------

def generate_bot_reply_sync(instance, bot_profile):
    """Синхронная генерация ответа бота """
    try:
        # If there was already an answer → exit
        if getattr(instance, "bot_replied", False):
            logger.info(f"[{bot_profile[
                'username']}] SKIP: bot already replied to comment {instance.id}"
                )
            return            
        
        username = bot_profile["username"]
        bot_user = ensure_bot_user(bot_profile)
        
        # проверка наличия настройки модели
        if not hasattr(settings,'LLM_MODEL') or not settings.LLM_MODEL:
            logger.error(f"[{username}] LLM_MODEL не настроен в settings")
            return
        
        # История последних 5 комментов
        recent_comments = Comment.objects.filter(
            post=instance.post).order_by("-created_at")[:5]
        dialogue = "\n".join(
            f"{c.author.username}: {c.content}" for c in reversed(recent_comments))
                       
        logger.info(f"[{username}] Готовлю ответ на коммент id={instance.id}")
        
        # chance to switch target from last to random
        target_comment = instance
        if random.random() < 0.3:
            target_comment = Comment.objects.filter(post=instance.post).order_by("?").first()
            
        # chance for a short interruption without generation
        if random.random() < 0.2:
            reply_text = random.choice([
                "лол", "гы", "сказал тоже мне", "ага-ага",
                "*зевает*", "*ржёт*", "*цокает языком*"
            ])
        else:           
        
            #  обработка ошибок подключения к Ollama
            try:
                client = get_ollama_client()
                response = client.chat(
                    model=settings.LLM_MODEL,
                        messages=[
                        {"role": "system", "content": bot_profile["style"]},
                        {"role": "user", "content": f"Вот обсуждение:\n{dialogue}\n\nОтветь на последний коммент в своём стиле. Кратко, метко, с характером."}
                    ],
                    stream=False
                )
            except Exception as ollama_error:
                logger.error(f"[{username}] Ошибка Ollama: {ollama_error}")
                reply_text = "🤷 Model is temporarily unavailable."
            else:
                reply_text =  clean_response(response["message"]["content"].strip())
                if not reply_text or len(reply_text) < 3:
                    reply_text = "🤷 Nothing to say."

            # имитация "подумал перед ответом"
            #time.sleep(random.randint(2, 6))
                
            # making response     
            bot_comment = Comment.objects.create(
                post=instance.post,
                author=bot_user,
                content=reply_text,
                bot_replied=True
            )
            
            # set a flag that there was a response to instance
            instance.bot_replied = True
            instance.save(update_fields=["bot_replied"])
            
            # push to WebSocket
            print(f"📡 CALL notify_new_comment for post=================={bot_comment.post_id}, id={bot_comment.id}")
            time.sleep(1)
            notify_new_comment(bot_comment)
            
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

        print(f"🎲 {bot['username']} chance={prob:.2f}, rolled={random.random()}")

        
        if random.random() < prob:
            logger.info(f"[{bot['username']}] Вероятность {prob:.2f} сработала — генерирую ответ.")
            run_task(generate_bot_reply_sync, instance.id, bot, use_celery_name="generate_bot_reply_task")
            logger.info(f"🚀 отправил задачу run_task для {bot['username']}")

        else:
            logger.debug(f"[{bot['username']}] Пропустил (p={prob:.2f})")
        
"""
#  profile
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
"""