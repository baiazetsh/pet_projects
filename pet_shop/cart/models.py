# cart/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from products.models import Product
from django.db.models import Q, UniqueConstraint, Index
from decimal import Decimal
from django.contrib.auth import get_user_model
User = get_user_model()


class Cart(models.Model):
    session_key = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name="session key",
        help_text = "session key for anonimous"
        )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="User",
        help_text="Authorized User"
        )
        
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)


    def merge_carts(self, source_cart):
        for source_item in source_cart.items.all():
            item, created = self.items.get_or_create(
                product = source_item.product,
                defaults = {'quantity': source_item.quantity}
            )
            if not created:
                item.quantity += source_item.quantity
                item.save()
        source_cart.delete()

    def __str__(self):
        if self.user:
            return f"Cart #{self.id} for {self.user.username}"
        return f"Cart #{self.id} for session {self.session_key}"


    @property
    def total_items(self):
        """Возвращает общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Возвращает общую стоимость товаров в корзине"""
        return sum(item.product.current_price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Cart"
    )
    product=models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product",
        help_text="Item from catalog"
        )
    quantity=models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Quantity",
        help_text="Quantity items in cart"
    )
    added_at= models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added at",
        help_text="Date add item in cart"
    )

    class  Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        ordering = ["-added_at"]
        constraints = [
            UniqueConstraint(fields=['cart', 'product'], name='uniq_cart_product')
        ]
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        """Возвращает общую стоимость позиции (цена × количество)"""
        return self.product.current_price * self.quantity

    def save(self, *args, **kwargs):
        """Проверяет доступность товара перед сохранением"""
        if not self.product.is_in_stock():
            raise ValidationError("Product is not available")
        super().save(*args, **kwargs)

    def clean(self):
        """Проверяет, что количество не превышает доступный остаток"""
        if self.quantity > self.product.stock:
            raise ValidationError(
                f"Requested quantity ({self.quantity}) exceeds available stock ({self.product.stock})"
            )

