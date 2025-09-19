# BLOGG/FORMS.PY

from django import forms
from django.forms import ModelForm
from .models import Topic, Post, Comment

class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ['name']
        label = {'author': ''}


class PostForm(ModelForm)        :
    class  Meta:
        model = Post
        fields = ['topic', 'header', 'text']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Your Comment'}

    def clean_text(self):
        text = self.cleaned_data.get('text')

        if not text or not text.strip():
            raise forms.ValidationError("Comments cannot be empty")
        
        return text