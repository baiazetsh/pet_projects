# zz/views

from django.forms import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import(
    UpdateView,
    CreateView,
    ListView,
    DetailView,
    FormView
)
import json
from celery.result import AsyncResult
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.views import View
from django.template.exceptions import TemplateSyntaxError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from icecream import ic

from django.db.models import Count

from zz.topic_provider import get_ready_topic



from .forms import(
CommentForm,
TopicForm,
ChapterForm,
PostForm,
ShitgenForm,
)
from .models import(Post,
Topic,
Chapter,
Comment,
Prompt,
GeneratedItem,
ChatMessage
)
from django.conf import settings
from zz.tasks import summarize_post
from zz.signals import call_ubludok
from zz.utils import notify_new_comment
from django.template import Template, Context
from zz.utils.ollama_client import generate_text, clean_response
from zz.utils.task_runner import run_task, run_shitgen_sync
from zz.utils.bots import BOTS


import logging
logger = logging.getLogger(__name__)


#обработка кнопки " позвать ублюдка"
def summon_ubludok(request, pk):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":             
        post = get_object_or_404(Post, pk=pk)  
              
        call_ubludok.send(sender=None, user=request.user, post=post)
        
        response = JsonResponse({
            "success": True,
            "message": f"The bastard is calledfor post:{post.id}"
        })
        response["Content-Type"] = "application/json"
        return response

    return JsonResponse({
        "success": False,
        "message": "wrong method"},
                        status=400
                        )



class SummarizePostView(View):
    """
    POST /api/posts/<id>/summary/
        → If summary already exists< return it immediately (without the task)
        → If not, start Celery and return the task_id

    GET /api/posts/<id>/summary/?task_id=<uuid>
        → Query Celery-task
    """
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        # Idempotent check — if summary exist already
        if post.summary and post.summary.strip():        
            return JsonResponse(
                {"status": "cached",
                "summary": post.summary
                }, status=200)
        # start Celery-task
        task = summarize_post.delay(post.id)
        return JsonResponse({
            "task_id": task.id,
            "status": "started"
        }, status=202)
    
    def get(self, request, pk):
        """Check the task status by task_id"""
        task_id  = request.GET.get("task_id")
        if not task_id:
            return JsonResponse({"error": "task_id is required"}, status=400)
            
        task_result = AsyncResult(task_id)
        
        match task_result.state:
            case "PENDING":
                return JsonResponse({"status": "pending"})
            case "STARTED":
                return JsonResponse({"status": "running"})
            case "FAILURE":
                error_message = str(task_result.info) if task_result.info else "Unknown error"
                return JsonResponse({
                    "status": "error",
                    "message": error_message
                    }, status=500)
            case "SUCCESS":
                # summary is already saved in Post, you can return it immediately
                post = get_object_or_404(Post, pk=pk)
                summary = post.summary or "Summarising is done, but result is empty"
                return JsonResponse({"status": "done", "summary": summary})

        # fallback
        return JsonResponse({"status": task_result.state}, status=200)


    

class TopicListView(LoginRequiredMixin, ListView):
    model =Topic
    template_name = "zz/index.html"
    context_object_name = "topics"
    paginate_by = 12
    
    def get_queryset(self):
        return Topic.objects.all().order_by('-created_at')
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
          # Предзагружаем главы для каждой темы
        topics_with_chapters = (
            Topic.objects.filter(
                owner=self.request.user,
                pk__in=[topic.pk for topic in context['topics']]
            )
            .prefetch_related('chapters__posts')
            .annotate(total_posts=Count('chapters__posts'))
        )
        
        
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
            comment.parent = Comment.objects.filter(id=parent_id, post=self.object).first()
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





class ShitgenView(View):
    def get(self, request):
        """Form render"""
        return render(request, "zz/shitgen_form.html", {"form": ShitgenForm()})

    def post(self, request):
        """ Frorm processing"""
        form = ShitgenForm(request.POST)

        if not form.is_valid():
            return render(request, "zz/shitgen_form.html", {"form": form})

        # Явное извлечение данных
        topic_theme = form.cleaned_data["topic_theme"]
        chapters = form.cleaned_data["chapters"]
        posts = form.cleaned_data["posts"]
        comments = form.cleaned_data["comments"]
        bot = form.cleaned_data["bot"]
        source = form.cleaned_data["source"]

        try:
            run_task(
                run_shitgen_sync,
                topic_theme=topic_theme,
                chapters=chapters,
                posts=posts,
                comments=comments,
                bot=bot,
                use_celery_name="generate_shitgen_task",
                source=source,
            )
            messages.success(request, f"Topic '{topic_theme}' generated successfully!")
            return redirect("zz:index")

        except Exception as e:
            logger.exception(f"[ShitgenView] Ошибка запуска: {e}")
            messages.error(request, "❌ Ошибка при запуске генерации")
            return render(request, "shitgen_form.html", {"form": form})


class ParseTopicAjaxView(View):
    """
    AJAX endpoint for parsing a trending topic.
    """
    def get(self, request):
        try:
            topic = get_ready_topic()
            if not topic:
                return JsonResponse({
                    "success": False,
                    "error": "No trending topics found."
                })
            return JsonResponse({"success": True, "topic": topic})
        except Exception as e:
            logger.exception("[ParseTopicAjaxView] Parsing error")
            return JsonResponse({"success": False, "error": str(e)})
        



class ChatView(View):
    template_name = "zz/chat.html"

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        bot_name = request.GET.get('bot', 'neuroubludok')  # Get selected bot from URL

        # Load chat history
        if user:
            # For authenticated users - load their messages
            messages_qs = ChatMessage.objects.filter(
                user=user,
                bot_name=bot_name
            ).order_by('-created_at')[:50]  # Last 100 messages
            
        else:
            # For anonymous users - load messages with user=None
            messages_qs = ChatMessage.objects.filter(
                user__isnull=True,
                bot_name=bot_name
            ).order_by('created_at')[:50]
        
        messages = list(messages_qs)[::-1]
        
        # Debug info
        logger.info(f"🔍 User: {user}, Bot: {bot_name}, Messages count: {messages_qs.count()}")
        
        return render(request, self.template_name, {
            "bots": BOTS,
            "history": list(messages),  # Convert to list for template
            "current_bot": bot_name
        })
        


class ChatClearAjaxView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        qs = ChatMessage.objects.filter(user=request.user)
        deleted, _ = qs.delete()
        logger.info(f"Clear all chats: deleted: {deleted} msgs (user={request.user})")
        return JsonResponse({"success": True, "deleted": deleted})

