#products/urls.py
from django.contrib import admin
from django.urls import include, path
from . import views


app_name = "products"

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name="product_detail"),
    path('category/<slug:slug>/', views.product_list, name='product_by_category'),
    path('product/<slug:slug>/', views.product_detail, name="product_detail"),
    path('search/', views.product_list, name="product_list")
]