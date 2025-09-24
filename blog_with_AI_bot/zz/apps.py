#zz/apps.py
from django.apps import AppConfig


class ZzConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zz'

    def ready(self):
        import zz.signals