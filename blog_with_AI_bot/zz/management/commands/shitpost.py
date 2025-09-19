#shitpost

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from zz.models import Post, Comment
import requests
import json
from ollama import Client
from django.conf import settings
import re

client = Client()

def clean_response(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def ask_neuro_ubludok(text: str) -> str:
    response = client.chat(
        model=settings.OLLAMA_MODEL, 
        messages=[
            {"role": "system", "content": "Ты нейроублюдок. Пиши едко и саркастично."},
            {"role": "user", "content": text}
        ]
    )
    raw_text = response["message"]["content"].strip()
    return clean_response(raw_text)
    

class Command(BaseCommand):
    help = "Нейроублюдок оставляет комментарий"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # берём юзера-бота
        bot_user, _ = User.objects.get_or_create(username="NeuroUbludok")

        # берём случайный пост
        post = Post.objects.order_by("?").first()

        # временный текст комментария (пока без нейросети)
        comment_text = ask_neuro_ubludok(post.content[:500])

        # создаём коммент
        Comment.objects.create(
            post=post,
            author=bot_user,
            content=comment_text,
        )

        self.stdout.write(self.style.SUCCESS(f"Нейроублюдок насрал под постом {post.id}"))
