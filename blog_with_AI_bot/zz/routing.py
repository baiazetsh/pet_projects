#zz/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    
    re_path(r"ws/posts/(?P<post_id>\d+)/$", consumers.CommentConsumer.as_asgi()),
    re_path(r"ws/comments/(?P<post_id>\d+)/$", consumers.CommentConsumer.as_asgi()),
    re_path(r"ws/shitgen/$", consumers.ShitgenConsumer.as_asgi()),
    re_path(r"ws/chat/$", consumers.ChatConsumer.as_asgi()),
]