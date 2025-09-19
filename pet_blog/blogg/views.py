#blogg/ views.py

from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Topic,Like
from .forms import TopicForm, PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    post = Post.objects.prefetch_related('likes_user')
     #Чтобы в шаблоне работало post.likes.all, нужно явно подгрузить лайки

    topics = Topic.objects.all()
    posts = Post.objects.all() # geltinng all posts from DB

    user_likes = set(
        Like.objects.filter(author=request.user).values_list("post_id", flat=True)
        )
    context = {'topics': topics, 
               'posts': posts,
               'user_likes': user_likes,
    }
    return render(request, 'blogg/index.html', context)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {'post': post,
                'comments':  post.comments.all(),
                'form': CommentForm(),

    }
    return render(request,'blogg/post_detail.html', context )


@login_required
def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(request.POST, request.FILES)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.author = request.user
            new_topic.save()

            return redirect('blogg:index')
    context = {'form': form, }
    return render (request, 'blogg/new_topic.html', context )


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
    else:
        form =PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

            return redirect('blogg:index')
    context = {'form': form}
    return render (request, 'blogg/new_post.html', context)

@login_required
def edit_post(request, post_id):
    pass

    context = {
        'post': post,
        'topic': topic,
        'form': form,
    }
    return render(request, 'blogg/edit_post.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "successfully")
            return redirect('blogg:post_detail', post_id=post.id)
        return redirect('blogg:post_detail', post_id=post.id)

def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id) # ищет лайк. Если не находит — создаёт.
    # Проверяем, есть ли уже лайк от этого пользователя
    like, created = Like.objects.get_or_create(author=request.user, post=post)

    if not created:
        # Если лайк уже был — удаляем (анлайк)
        like.delete()
     # Если created=True — лайк уже добавлен
     # Возвращаемся туда, откуда пришли
    return redirect(request.META.get('HTTP_REFERER', 'blogg:index'))



