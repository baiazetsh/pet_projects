from django.contrib import admin
from .models import Chat, Message, Like
from users.models import UserProfile

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Like)
admin.site.register(UserProfile)
# Register your models here.
