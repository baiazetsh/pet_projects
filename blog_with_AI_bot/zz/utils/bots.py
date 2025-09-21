#utils/bots.py
import re
import requests
from django.conf import settings
import logging
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)


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

