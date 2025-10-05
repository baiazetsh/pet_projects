#zz/urls
from django.urls import path
from . import views

app_name = "zz"

urlpatterns =[
    path("", views.TopicListView.as_view(), name='index'),
    path("topics/create/", views.TopicCreateView.as_view(), name="topic_create"),
    path('topics/<int:pk>/update/', views.TopicUpdateView.as_view(), name='topic_update'),
    path('topics/<int:pk>/delete/', views.TopicDeleteView.as_view(), name="topic_delete"),
    path('topics/<int:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),
    
    
    path("topics/<int:topic_id>/chapters/create/", views.ChapterCreateView.as_view(), name="chapter_create"),
    path('chapters/<int:pk>/', views.ChapterDetailView.as_view(), name='chapter_detail'),
    path('chapters/<int:pk>/update/', views.ChapterUpdateView.as_view(), name='chapter_update'),
    path('chapters/<int:pk>/delete/', views.ChapterDeleteView.as_view(), name="chapter_delete"),
    
    
    path("chapter/<int:chapter_id>/posts/create/", views.PostCreateView.as_view(), name="post_create"),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name="post_delete"),
    
    
    path("posts/<int:pk>/summon/", views.summon_ubludok, name="summon_ubludok"),
    path("posts/<int:pk>/summarize/", views.SummarizePostView.as_view(), name="post_summarize"),


    #path("prompts/manual/", views.PromptInlineView.as_view(), name="prompt_execute_inline"),
    path("shitgen/", views.ShitgenView.as_view(), name="shitgen_form"),
    path("chat/", views.ChatView.as_view(), name="chat"),
    path("chat/clear/", views.ChatClearAjaxView.as_view(), name="chat_clear"),
]