class TopicUpdateView(LoginRequiredMixin, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = 'zz/topic_form.html'
    success_url = reverse_lazy('zz:index')
    
    def get_object(self, queryset = None):
        obj = get_object_or_404(Topic, pk=self.kwargs['pk'])
        if obj.owner != self.request.user:
            raise PermissionDenied(_("You can't edit this topic"))
        return obj
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs
        
    def form_valid(self, form):
        messages.success(self.request, _('Topic updated successfully'))
        return super().form_valid(form)
    
class TopicDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        if topic.owner != request.user:
            raise PermissionDenied("You can't delete this topic")
        
        topic.delete()
        messages.success(request, "Topic deleted successfully")
        return redirect("zz:index")
    
    
    
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
                'authofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placholder': _('Enter the description of chapter'),
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


def get_success_url(self):
        return reverse_lazy(
            "zz:chapter_detail", kwargs={"pk": self.object.chapter.pk}
        )        
        
class ChapterUpdateView(LoginRequiredMixin, UpdateView):
    model = Chapter
    form_class = ChapterForm
    template_name = 'zz/chapter_form.html'
    
    def get_object(self, queryset = None):
        obj = get_object_or_404(Chapter, pk=self.kwargs["pk"])
        if obj.topic.owner != self.request.user:
            raise PermissionDenied(_("You can't update this chapter"))
        return obj
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _("Chapter updated"))
        return super(). form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = self.object.topic #add topic into the context!
        return context
    
    def get_success_url(self) -> str:
        return reverse_lazy("zz:topic_detail", kwargs={"pk": self.object.topic.pk})
            
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
                'authofocus': True,
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