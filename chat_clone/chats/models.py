#chats/models/py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()
class Chat(models.Model):
    author = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="created_chats"
)
    participants = models.ManyToManyField(
        User,
        related_name='chats',
        verbose_name='Participants',
    )
    topic = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        )
    text = models.TextField(verbose_name="Text")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.topic}'

    class Meta:
        verbose_name='Chat'
        verbose_name_plural='Chats'
        ordering =['-updated_at']

class Message(models.Model):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Chat",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Author",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.text[:30]}..."

    class Meta:
        verbose_name="Message"
        verbose_name_plural="Messages"
        ordering=['created_at']

class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author','message'], name="unique_like")
            ]
        
        def __str__(self):
            return f'{self.author.username} liked {self.message.text}'