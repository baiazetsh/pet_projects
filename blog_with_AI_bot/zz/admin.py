from django.contrib import admin

from .models import Topic, Chapter, Post, Comment

admin.site.register(Topic)
admin.site.register(Chapter)
admin.site.register(Post)
admin.site.register(Comment)