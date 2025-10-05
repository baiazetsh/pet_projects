from dataclasses import fields
from django import forms

from django.utils.translation import gettext_lazy as _
from django.template import Template
from django.template.exceptions import TemplateSyntaxError
from django.conf import settings

from zz.utils.bots import BOTS, BOT_USERNAMES
from .models import Comment, Topic, Chapter, Post, Prompt, GeneratedItem




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


class PromptForm(forms.ModelForm): 
    class Meta:
        model = Prompt
        fields = [
            "title",
            "template",
            "model_name",
            "tags",
            "status",
        ]
        widgets = {
            "template": forms.Textarea(attrs={
                "rows": 6,
                "placeholder": "Enter the template with variables, for example: {{ topic }} - is very important"
            }),
            "tags": forms.TextInput(attrs={
                "placeholder": "summary, comment, post"
            }),
        }

    def clean_template(self):
        template_str = self.cleaned_data["template"]
        try:
            Template(template_str)
        except TemplateSyntaxError as e:
            raise ValidationError(f"Invalid template syntax: {e}")
        return template_str




class ShitgenForm(forms.Form):
    topic_theme = forms.CharField(
        label="Topic theme",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )

    chapters = forms.IntegerField(
        label="Number of chapters",
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    posts = forms.IntegerField(
        label="Posts per chapter",
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    comments = forms.IntegerField(
        label="Comments per post",
        min_value=0,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    bot = forms.ChoiceField(
        label="Bot character",
        choices=[(b["username"], b["display_name"]) for b in BOTS],
        widget=forms.Select(attrs={"class": "form-select"}),
        initial=BOTS[0]["username"],  # по умолчанию берём первого бота из списка
    )
