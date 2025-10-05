from django.urls import reverse
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

class Topic(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name =  "topics",
        verbose_name="Author",
        )
    name = models.CharField(
        max_length=200,)
    created_at = models.DateTimeField(auto_now_add=True, null=True,
    )
    
    
    class Meta:
        verbose_name= _("topic")
        verbose_name_plural=_("topics")
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='unique_topic_per_owner')
        ]
        
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self):
        return reverse('zz:topic_detail', kwargs={'pk': self.pk})



class Chapter(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete = models.CASCADE,
        related_name="chapters",
        verbose_name=_("Topic"),
        )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Title chapter"),
    )
    description = models.CharField(max_length=300, null=True)
    order = models.PositiveIntegerField(
        verbose_name=_("Order"),
        default=0,
        help_text=_("Use for sorting chapters"),
    )
    author = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="authored_chapters",
    verbose_name=_("Author"),
    )

    class Meta:
        verbose_name = _("Chapter")
        verbose_name_plural = _("Chapters")
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['topic', 'title'], name='unique_chapter_per_topic')
        ]
        

    def __str__(self):
        return f"{self.topic.name} ->{self.title}"
        
    def get_absolute_url(self):
        return reverse('zz:chapter_detail', kwargs={'pk': self.pk})
    
        
        
class Post(models.Model):
    chapter = models.ForeignKey(
        Chapter,
        on_delete = models.CASCADE,
        related_name="posts",
        verbose_name=_("Chapter"),
    )
    title=models.CharField(
        max_length=200,
        verbose_name=_("Title of post"),
    )
    content=models.TextField(
        verbose_name=_("Content"),
    )
    created_at=models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(
        verbose_name=_("Order"),
        default=0,
        help_text=_("Use for sort posts in chapter")
            )
    summary = models.TextField(blank=True, null=True)
    author = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="posts",
    verbose_name=_("Author"),
)


    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['chapter', 'title'], name='unique_post_per_chapter')
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('zz:post_detail', kwargs={'pk': self.pk})



class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Post"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Author"),
    )
    parent=models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name="replies"                     ,
        null=True,
        blank=True,
        verbose_name=_("Patent comment"),
        )
    
    content = models.TextField(
        max_length=600,
        verbose_name=_("Content"),
        )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
    )
    bot_replied = models.BooleanField(default=False)
    toxicity_score = models.FloatField(default=0.0)
    
    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ['created_at']
        
    def __str__(self):
        return f"Comment by {self.author.username}: {self.content[:20]} on {self.post.title}"
    
    def get_absolute_url(self):
        return reverse('zz:post_detail', kwargs={'pk': self.post.pk})
    
    @property
    def is_root(self):
        return self.parent is None
    

class Prompt(models.Model):
    title = models.CharField(max_length=250)
    template = models.TextField(help_text=_("Template with variables, for exsample: {{ topic }}"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        verbose_name = _("Author")
        )
    model_name = models.CharField(
        max_length=30,
        help_text=_("LLM model name"),
        default=getattr(settings, "LLM_MODEL")
        )
    tags = models.CharField(max_length=200, blank=True, help_text="Thru comma: summary, comment, post")

    #Statuses
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("ready", "Готово"),
        ("used", "Использовано"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft"
    )

    def extract_variables(self):
        import re
        return re.findall(r"\{\{\s*(\w+)\s*\}\}", self.template)

    def render_with(self, context: dict) -> str:
        from django.template import Template, Context
        return Template(self.template).render(Context(context))

    def __str__(self):
        return self.title
    

class GeneratedItem(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_items",
        )
    inputs = models.JSONField()  # значения переменных
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("bot", "Bot"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        null=True, blank=True
    )
    bot_name = models.CharField(max_length=50, default="NeuroUbludok")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"



