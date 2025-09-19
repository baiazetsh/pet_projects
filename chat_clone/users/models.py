#users/models.py
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        related_name = "profile",
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
        )
    bio = models.TextField(max_length=500, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username