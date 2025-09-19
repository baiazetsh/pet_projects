 # blog/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Topic(models.Model):
    name = models.CharField(max_length=50)
    author = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name="topics",
                                verbose_name="Author")
    
    def __str__(self):
        return self.name
    
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               verbose_name="Author" )
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT,
                              null=False,
                              blank=False,related_name="posts", verbose_name="Topic" )
    header = models.CharField(max_length=50)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.header
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                              related_name="comments", verbose_name="Post")                             
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Author")
    text = models.CharField(max_length=300, verbose_name="Comment text")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        text_preview = self.text[:20]
        if len(self.text) > 20:
            text_preview += "..."
        return f"{text_preview} - {self.author.username}"


class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'post'], name='unique_like') 
        ] # one author(user)-> one like

    def __str__(self):
        return f'{self.author.username} liked {self.post.header}'
        
