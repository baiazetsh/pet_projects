from dataclasses import fields
from django import forms
from .models import Comment, Topic, Chapter, Post
from django.utils.translation import gettext_lazy as _

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']  # ← owner будет устанавливаться автоматически из request.user
        labels = {
            'name': _('Название темы'),
        }
        help_texts = {
            'name': _('Введите название темы (максимум 200 символов).'),
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите название темы...'),
                'autofocus': True,
            }),
        }
        
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                    widget_class = self.fields[field].widget.attrs.get('class', '')
                    self.fields[field].widget.attrs['class']  =f"{widget_class} is-invalid".strip()
                    
    
    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        
        if not name:
            raise forms.ValidationError(_('Name cannot be empty'))
        
        if self.owner:
            if Topic.objects.filter(owner=self.owner, name__iexact=name)\
                .exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(
                    _('You have the same name topic already "%(name)s". Chose other topic'),
                    params={'name': name},
                )
        return name
                
class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['title', 'description']  # ← owner будет устанавливаться автоматически из request.user
        labels = {
            'title': _('Name of chapter'),
            'description': _("Description")
        }
        help_texts = {
            'title': _('Введите название главы (максимум 200 символов).'),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите название главы...'),
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Enter the description of chapter'),
                'rows': 3,
            })
        }  
        
    def __init__(self, *args, owner=None, **kwargs):   
        super().__init__(*args, **kwargs)         
        self.owner = owner
        
        print("--------------------DEBUG: ChapterForm init called with owner =", owner)
        
        
    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if Chapter.objects.filter(topic__owner=self.owner, title__iexact=title)\
                            .exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(("You have the chapter with same title already"))                    
        return title
        
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']  # ← owner будет устанавливаться автоматически из request.user
        labels = {
            'title': _('Название поста'),
                        
        }
        help_texts = {
            'title': _('Введите название поста (максимум 200 символов).'),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите название поста...'),
                'autofocus': True,
            }),
        'content': forms.Textarea(attrs={
            'class': 'form-control',
        })
        }
        
    def __init__(self, *args, **kwargs):            
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        
        
    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if Post.objects.filter(
            chapter__topic__owner=self.owner,
            title__iexact=title
        ).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError("You have the chapter with same title already")
        return title
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': _('Enter the comment text')
        }
        widgets = {            
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Enter the comment text'),
                'authofocus': True,
                'rows': 3,
            })
        }
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)