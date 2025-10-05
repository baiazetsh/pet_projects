from django.contrib import admin

from zz.models import(
    Topic,
    Chapter,
    Post,
    Comment,
    Prompt,
    GeneratedItem,
    ChatMessage,
    
)
from users.models import(
    Profile,
)
from .forms import PromptForm

admin.site.register(Topic)
admin.site.register(Chapter)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(ChatMessage)

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    form = PromptForm
    list_display = ["title", "model_name", "status", "author", "created_at"]
    list_filter = ["status", "model_name", "tags", "author"]
    search_fields = ["title", "template"]
    readonly_fields = ["created_at", "updated_at"]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_bot", "quote")
    search_fields = ("user__username", "bio", "quote")
