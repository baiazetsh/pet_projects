#chats/urls.py

from django.urls import path
from .import views

app_name = "chats"

urlpatterns = [
    path('', views.index, name="index"),
    path('new_chat/', views.new_chat, name="new_chat"),
    path('<int:chat_id>/new_message/', views.new_message, name="new_message"),
    path('like/<int:message_id>/', views.toggle_like, name="toggle_like"),
    path('<int:chat_id>/', views.chat_detail, name="chat_detail"),
]