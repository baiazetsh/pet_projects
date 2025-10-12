#zz/utils/task_runner.py

import logging
import threading
from django.conf import settings
from zz.utils.source_selector import get_active_source
from django.core.management import call_command

logger = logging.getLogger(__name__)

try:
    from zz import tasks
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False

#source = get_active_source()

def run_task(func, *args, use_celery_name=None, **kwargs):
    """
    Универсальный запуск задачи.

    :param func: функция для синхронного запуска (например run_shitgen_sync или generate_bot_reply_sync)
    :param args: позиционные аргументы
    :param kwargs: именованные аргументы
    :param use_celery_name: имя задачи в zz/tasks.py (например "generate_shitgen_task" или "generate_bot_reply_task")

    Если USE_CELERY включён и задача найдена → запустим через Celery.
    Иначе → через threading.
    """

    if getattr(settings, "USE_CELERY", False) and HAS_CELERY and use_celery_name:
        celery_task = getattr(tasks, use_celery_name, None)
        if celery_task:
            logger.info(f"[TsakRunner] -> Celery ({use_celery_name})")
            celery_task.delay(*args, **kwargs)
            return
        else:
            logger.warning(f"[TaskRunner] Celery-task {use_celery_name} not found< fallback -> threading")

        # fallback threading
    logger.info(f"[TaskRunner] → threading ({func.__name__})")
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    
    
    
# for ShitgenView
def run_shitgen_sync(
    topic_theme,
    chapters=1,
    posts=1,
    comments=1,
    bot="NeuroUbludok",
    source=None
):

    """Синхронный запуск shitgen через call_command (для threading fallback)."""
    if not source:
        source = get_active_source()
        
    call_command(
        "shitgen",
        topic_theme,
        #chapters=chapters,
        #posts=posts,
        #comments=comments,
        #bot=bot,
        f"--chapters={chapters}",
        f"--posts={posts}",
        f"--comments={comments}",
        f"--bot={bot}",
        f"--source={source}",        
    )
    