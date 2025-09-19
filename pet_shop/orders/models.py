#orders/orders.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone  # добавил для корректной работы mark_as_paid
from products.models import Product
from decimal import Decimal
from django.contrib.auth import get_user_model
User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Карта'),
        ('paypal', 'PayPal'),
        ('cod', 'Наличные при получении'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True
        )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        db_index=True,
        choices=STATUS_CHOICES,
        default="pending")

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators = [MinValueValidator(0.01)]
        )
    shipping_address = models.TextField(help_text="Delivery address")
    billing_address = models.TextField(
        blank=True,
        null=True,
        help_text="Paynment address(If diffirent to delivery)"
         )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
        )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text="Transaction ID"
        )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Comments"
        )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        user_display = self.user.username if self.user else "Guest"
        return f"Order #{self.id} - {user_display}({self.status})"

    def recalc_total(self):
        """Recalculate order total from items"""
        self.total_price = sum(item.total_price for item in self.items.all())
        self.save(update_fields=["total_price"])



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete = models.CASCADE,
        related_name = "items",
        help_text = "Linked order"
        )
    product = models.ForeignKey(
        Product,
        on_delete = models.CASCADE,
        null = True,
        blank = True,
        help_text = "Item"
    )
    name = models.CharField(
        max_length = 255,
        help_text = "Item's name at time of purchase "
    )
    price = models.DecimalField(
        max_digits = 8,
        decimal_places = 2,
        validators = [MinValueValidator(0.00)],
        help_text = "Unit price at time of purchase."
    )
    quantity = models.PositiveIntegerField(
        validators = [MinValueValidator(1)],
        help_text = "Quantity units item"
    )
    total_price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        validators = [MinValueValidator(Decimal(0.00))],
        help_text = "Total cost of string(price x quantity)"
    )

    class Meta:
        verbose_name = "Order position"
        verbose_name_plural = "Order positions"

    def __str__(self):
        return f"{self.quantity} x {self.name} in order #{self.order.id}"

    def save(self, *args, **kwargs):
          # Автоматически вычисляем total_price при сохранении
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

