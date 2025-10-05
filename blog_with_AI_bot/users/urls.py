# users/urls.py
from django.urls import path
from . import views
from .api import ProfileDetailAPI 

app_name ="users"

urlpatterns =[
    #path("", views.ProfileListView.as_view(), name="profile_list"),
    path("<int:pk>/", views.ProfileDetailView.as_view(), name="profile_detail"),
    path("profile/<int:pk>/", views.ProfileDetailView.as_view(), name="profile_detail"),
    path("api/profiles/<int:pk>/", ProfileDetailAPI.as_view(), name="profile_detail_api"),
]