from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Task(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    description = models.TextField(blank=True, verbose_name="Description")
    status = models.BooleanField(default=False, verbose_name="Complete")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Due Date"
    )
    owner = models.ForeignKey(User,
    on_delete=models.CASCADE,
    related_name="tasks", 
    verbose_name="Owner"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.title} - {self.owner.username}"

    def is_overdue(self):
        """Проверяет, просрочена ли задача"""
        if self.due_date:
            return self.due_date < timezone.now().date() and not self.status
        return False
