#zz/utils/task_runner.py

import logging
import threading
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from zz import tasks
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False


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