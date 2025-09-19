#weather/urls.py

from django.urls import path
from . import views

app_name = "weather"

urlpatterns = [
    path('', views.weather_view, name="weather"),
    path('export/json/', views.export_json, name="export_json"),
    path('export/cvs/', views.export_csv, name="export_cvs"),

]