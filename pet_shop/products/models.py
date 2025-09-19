#products/models.py
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True,
        max_length=255, blank=True)
    image = models.ImageField(upload_to='categories/')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]  # сортировка категорий по имени

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)])
    stock = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)])
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)])

    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def is_in_stock(self):
        return self.stock >0

    @property
    def current_price(self):
        return self.price - self.discount