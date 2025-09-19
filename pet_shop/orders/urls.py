#orders/urls.py
from django.contrib import admin
from django.urls import include, path
from . import views


app_name = "orders"

urlpatterns = [
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:id>/pay/', views.order_pay, name="order_pay"),
    path('orders/my_orders/', views.order_list, name="order_list"),
    path('<int:id>/review/', views.order_review, name="order_review"),

]