#products/views.py
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from cart.models import Cart, CartItem
from .models import Product, Category
from cart.forms import AddToCartForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q



def product_list(request, slug=None):
    list_categories = Category.objects.all()
    list_products = Product.objects.select_related('category').all() #.order_by("category__name", "name")
    # если поле — это ForeignKey, то доступ к его полям
    # в запросах делается через __ (два подчёркивания),

    # Текущая категория (если есть slug)
    current_category = None
    if slug:
        current_category = get_object_or_404(Category, slug=slug)
        list_products = list_products.filter(category=current_category)
    
    # Поиск по имени/описанию
    q = request.GET.get('q','').strip()
    if q:
        list_products = list_products.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )
        if not list_products.exists():
            messages.info(request, "No results  found")
    
    # Фильтрация по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')


    if min_price:
        try:
            list_products = list_products.filter(price__gte=float(min_price))
        except ValueError:
            messages.warning(request, "Invalid min_price")

    if max_price:
        try:
            list_products = list_products.filter(price__lte=float(max_price))
        except ValueError:
            messages.warning(request, "Invalid max_price")

    # проверка на пустые результаты после всех фильтраций
    if q and not list_products.exists():
        messages.info(request, "No results found")

    # Сортировка
    sort = request.GET.get('sort', 'name')
    allowed_sorts = ['name', '-name', 'price', '-price', 'created_at', '-created_at']
    if sort in allowed_sorts:
        list_products = list_products.order_by(sort)
    else:
        list_products = list_products.order_by('name')

    # Пагинация
    paginator = Paginator(list_products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'list_products': page_obj.object_list,
        'list_categories': list_categories,
        'current_category': current_category,
        'search_query': q,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    current_product = get_object_or_404(Product, id=product_id)

    context = {
        'current_product': current_product,
        'form': AddToCartForm(),
    }

   

    return render(request, 'products/product_detail.html', context)


