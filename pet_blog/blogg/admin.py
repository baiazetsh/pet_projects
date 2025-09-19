from django.contrib import admin
from .models import Post, Topic, Comment
admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(Comment)