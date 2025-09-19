#cart/urls.py
from django.contrib import admin
from django.urls import include, path
from . import views


app_name = "cart"

urlpatterns = [
    path('cart_detail/', views.cart_detail, name="cart_detail"),
    path('add/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]