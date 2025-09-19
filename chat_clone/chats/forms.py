#chats/forms.py
from django import forms
from django.forms import ModelForm
from .models import Chat, Message

class ChatForm(ModelForm):
    class Meta:
        model = Chat
        fields = ['topic', 'text', 'participants']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['text']