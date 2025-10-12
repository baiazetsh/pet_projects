#zz/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages

from zz.models import(
    Topic,
    Chapter,
    Post,
    Comment,
    Prompt,
    GeneratedItem,
    ChatMessage,
    GenerationSettings,
    ParsedTopic,
    GeneratedChain
    
)
from users.models import(
    Profile
)
from .forms import PromptForm
from zz.tasks import fetch_trending_topics, generate_chains_for_new_topics


admin.site.register(Topic)
admin.site.register(Chapter)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(ChatMessage)
admin.site.register(GeneratedItem)

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

@admin.register(GenerationSettings)
class GenerationSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "current_source", "updated_at")
    list_editable = ("current_source",)    


@admin.register(ParsedTopic)
class ParsedTopicAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "title_clean", "score", "comments", "processed", "created_at")
    list_filter = ("source", "processed")
    search_fields = ("title_raw", "title_clean")

    change_list_template = "zz/parsedtopic_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("run_pipeline/", self.admin_site.admin_view(self.run_pipeline), name="run_topic_pipeline"),
        ]
        return custom_urls + urls

    def run_pipeline(self, request):
        fetch_trending_topics.delay()
        generate_chains_for_new_topics.delay()
        self.message_user(request, "🚀 Пайплайн запущен!", level=messages.SUCCESS)
        return redirect("..")