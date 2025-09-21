from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Topic(models.Model):
    owner = models.ForeignKey(
        User,
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
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Author"),
    )
    parent=models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
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
    
    
    