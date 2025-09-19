from django.contrib import admin
from .models import Product, Category
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

prepopulated_fields = {"slug": ("name",)}


