# blogg/ urls.py
from django.urls import path
from .import views

app_name = 'blogg'

urlpatterns = [
    path("", views.index, name='index'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('new_topic/', views.new_topic, name="new_topic"),
    path('new_post/', views.new_post, name="new_post"),
    path('add_comment/<int:post_id>/', views.add_comment, name="add_comment"),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    
    ]
