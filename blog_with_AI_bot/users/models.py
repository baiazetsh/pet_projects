# users/models.py
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.templatetags.static import static


class Profile(models.Model):
    user = models.OneToOneField(
            settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE,
                            related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        default='avatars/defaultava.png'
        
    )
    bio = models.TextField(max_length=500, blank=True)
    quote = models.CharField(max_length=200, blank=True)
    is_bot = models.BooleanField(
        default=False,
        help_text="If True - is it bot, not a human"
    )

    def __str__(self):
        return f"Profile of {self.user.username} (bot: {self.is_bot})"

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else settings.MEDIA_URL + 'avatars/default.png'

    """
    @property
    def avatar_url(self):
        # Если пользователь загрузил аватар в MEDIA
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        # Если у бота — используем статические аватарки
        if self.is_bot:
            mapping = {
                "NeuroBatya": static("images/neurobatya.png"),
                "NeuroPsina": static("images/neuropsina.png"),
                "NeuroUbludok": static("images/neuroubludok.png")
            }
            return mapping.get(self.user.username, static("images/defaultava.png"))
        # Для обычных юзеров дефолт
        return static("images/defaultava.png")
    """    