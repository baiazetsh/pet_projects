# managerr/urls.py
from django.urls import path
from .import views

app_name = "managerr"

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/new/', views.task_new, name='task_new'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
]