# zz/views
from urllib import request
from django.db.models.fields import json
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CommentForm, TopicForm, ChapterForm, PostForm
from .models import Post, Topic, Chapter, Comment
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.views import View
from django.conf import settings
from zz.tasks import summarize_post
from zz.signals import call_ubludok
from celery.result import AsyncResult
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from zz.utils import notify_new_comment
import json

#обработка кнопки " позвать ублюдка"
def summon_ubludok(request, pk):
    if request.method == "POST":             
        post = get_object_or_404(Post, pk=pk)  
              
        call_ubludok.send(sender=None, user=request.user, post=post)
        
        return JsonResponse({
            "success": True,
            "message": f"The bastard is calledfor post:{post.id}"
            })
    return JsonResponse({
        "success": False,
        "message": "wrong method"},
                        status=400
                        )


class SummarizePostView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        task = summarize_post.delay(post.id)
        return JsonResponse({"task_id": task.id, "status": "started"})
    
    def get(self, request, pk):
        """Check the task status by task_id"""
        task_id  = request.GET.get("task_id")
        if not task_id:
            return JsonResponse({"error": "task_id is required"}, status=400)
            
        task_result = AsyncResult(task_id)
        
        if task_result.state == "PENDING":
            return JsonResponse({"status": "pending"})
        elif task_result.state == "STARTED":
            return JsonResponse({"status": "running"})
        elif task_result.state == "FAILURE":
            error_message = str(task_result.info) if task_result.info else "Unknown error"
            return JsonResponse({"status": "error", "message": str(task_result.info)})
        elif task_result.state == "SUCCESS":
            # summary is already saved in Post, you can return it immediately
            post = get_object_or_404(Post, pk=pk)
            summary = post.summary or "Summarising is done, but result is empty"
            return JsonResponse({"status": "done", "summary": summary})

        return JsonResponse({"status": task_result.state})
    

class TopicListView(LoginRequiredMixin, ListView):
    model =Topic
    template_name = "zz/index.html"
    context_object_name = "topics"
    paginate_by = 3
    
    def get_queryset(self):
        return Topic.objects.all().order_by('-created_at')
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
          # Предзагружаем главы для каждой темы
        topics_with_chapters = Topic.objects.filter(
            owner=self.request.user,
            pk__in=[topic.pk for topic in context['topics']]
        ).prefetch_related('chapters')
        context['topic_with_chapters'] = topics_with_chapters
        return context

class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm
    template_name = 'zz/topic_form.html'
    success_url = reverse_lazy('zz:index')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, _("Topic created successfully"))
        return super().form_valid(form)

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
    
class TopicDetailView(LoginRequiredMixin, DetailView):
    model = Topic
    template_name = 'zz/topic_detail.html'
    context_object_name = 'topic'
    
    def get_queryset(self):
        return Topic.objects.all().order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['chapters'] = self.object.chapters.prefetch_related(
            'posts').order_by('order')
        return context
    
class ChapterDetailView(LoginRequiredMixin, DetailView):
    model = Chapter
    template_name = 'zz/chapter_detail.html'
    context_object_name = 'chapter'
    
    def get_queryset(self):
        return Chapter.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.order_by('order')
        return context
    

    
class ChapterCreateView(LoginRequiredMixin, CreateView):
    model = Chapter
    form_class = ChapterForm
    template_name = 'zz/chapter_form.html'
    
    def form_valid(self, form):
        form.instance.topic = get_object_or_404(
            Topic,
            pk=self.kwargs['topic_id'],
            owner=self.request.user
        )
        messages.success(self.request, _("Chapter created successfully"))
        return super().form_valid(form)    
    
    def get_success_url(self):
        return reverse_lazy(
            'zz:topic_detail', kwargs={'pk': self.object.topic.pk}
            )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topic"] = get_object_or_404(
            Topic,
            pk=self.kwargs["topic_id"],
            owner=self.request.user
        )
        return context
    

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'zz/post_form.html'
    
    def form_valid(self, form):
         # достаём главу, проверяем владельца через связанный Topic
        chapter = get_object_or_404(
            Chapter,
            pk=self.kwargs['chapter_id'],
            topic__owner=self.request.user
        )
        form.instance.chapter = chapter
        messages.success(self.request, _("Post created successfully"))        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy(
            "zz:chapter_detail", kwargs={"pk": self.object.chapter.pk}
        )
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chapter"] = get_object_or_404(
            Chapter,
            pk=self.kwargs["chapter_id"],
            topic__owner=self.request.user
        )
        return context
    
    
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
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = self.object.topic #add topic into the context!
        return context
    
    def get_success_url(self) -> str:
        return reverse_lazy("zz:topic_detail", kwargs={"pk": self.object.topic.pk})
    

class ChapterDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chapter = get_object_or_404(Chapter, pk=pk)
        if chapter.topic.owner != request.user:
            raise PermissionDenied("You can't delete this chapter")
        
        topic_pk = chapter.topic.pk  #saving id topic
        chapter.delete()
        messages.success(request, "Chapter deleted")
        return redirect("zz:topic_detail", pk=topic_pk)
    
# zz/views.py
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import Post, Comment
from .forms import CommentForm
from zz.utils import notify_new_comment


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'zz/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = (
            Comment.objects.filter(post=self.object, parent__isnull=True)
            .select_related('author')
            .order_by('-created_at')
        )
        context['form'] = CommentForm()
        context['chapter'] = getattr(self.object, "chapter", None)
        return context

    def post(self, request, *args, **kwargs):
        """Создание комментария через AJAX"""
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if not form.is_valid():
            return JsonResponse({
                "success": False,
                "errors": form.errors,
            }, status=400)

        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = request.user
        parent_id = request.POST.get("parent_id")
        if parent_id:
            comment.parent = Comment.objects.filter(id=parent_id).first()
        comment.save()

        # пушим всем по WebSocket
        notify_new_comment(comment)

        return JsonResponse({
            "success": True,
            "comment": {
                "id": comment.id,
                "author": comment.author.username,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "parent_id": comment.parent.id if comment.parent else None,
            }
        })
    

"""
class PostDetailView(DetailView):
    model = Post
    template_name = 'zz/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            post=self.object
        ).select_related('author').order_by('-created_at')
        context['form'] = CommentForm()
        context['chapter'] = getattr(self.object, 'chapter', None)
        return context

    def post(self, request, *args, **kwargs):
        #Создание комментария — всегда JSON
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()

            # пушим в WebSocket
            notify_new_comment(comment)

            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'author': comment.author.username,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat(),
                }
            })

        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    

  
class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'zz/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.order_by('-created_at')
    
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get("parent_id")
            if parent_id:
                comment.parent = Comment.objects.filter(id=parent_id).first()
            
            comment.save()
            
            # 🔥 уведомляем WebSocket-группу
            from zz.utils import notify_new_comment
            notify_new_comment(comment)
            
            return JsonResponse({
                "success": True,
                "comment": {
                    "id": comment.id,
                    "author": comment.author.username,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                }
            })
        
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
            
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
         # self.object уже есть, это текущий Post
        context["chapter"] = self.object.chapter
        context["topic"] = self.object.chapter.topic
        context["comments"] = self.object.comments.filter(parent__isnull=True).order_by("-created_at")
        context["form"] = CommentForm()
        
        return context

# В zz/views.py найдите и замените PostDetailView на эту версию:

class PostDetailView(DetailView):
    model = Post
    template_name = 'zz/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            post=self.object
        ).select_related('author').order_by('created_at')
        context['form'] = CommentForm()
        
        # Получаем chapter для отображения в шаблоне
        try:
            context['chapter'] = self.object.chapter
        except AttributeError:
            context['chapter'] = None
            
        return context
    
    def post(self, request, *args, **kwargs):
        #Обработка POST запросов (создание комментариев)
        self.object = self.get_object()
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            
            # Отправляем WebSocket уведомление
            notify_new_comment(comment)
            
            # Проверяем, AJAX ли это запрос
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'id': comment.id,
                        'author': comment.author.username,
                        'content': comment.content,
                        'created_at': comment.created_at.isoformat(),
                    }
                })
            else:
                # Обычный POST запрос - редирект
                messages.success(request, _('Comment added successfully!'))
                return redirect('zz:post_detail', pk=self.object.pk)
        else:
            # Форма невалидна
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            else:
                # Показываем форму с ошибками
                context = self.get_context_data()
                context['form'] = form
                return self.render_to_response(context)
"""
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "zz/post_form.html"
    
    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, pk=self.kwargs["pk"])
        if obj.chapter.topic.owner != self.request.user:
            raise PermissionDenied(_("You can't update this chapter"))
        return obj
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _("Post updated"))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chapter'] = self.object.chapter
        context['topic'] = self.object.chapter.topic        
        return context
    
    def get_success_url(self):
        return reverse_lazy(
            "zz:chapter_detail",
            kwargs={"pk": self.object.chapter.pk})

    
class PostDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.chapter.topic.owner != request.user:
            raise PermissionDenied("You can't delete this post")
        
        chapter_pk = post.chapter.pk
        post.delete()
        messages.success(request, "Post deleted")
        return redirect("zz:chapter_detail", pk=chapter_pk)