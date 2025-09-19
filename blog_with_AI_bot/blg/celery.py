# celery.py
import os
from celery import Celery

# Указываем Django настройки по умолчанию
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blg.settings")

# Создаём объект Celery, имя = имя проекта
app = Celery("blg")

# Берём все настройки с префиксом CELERY_ из settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически искать tasks.py во всех приложениях
app.autodiscover_tasks()