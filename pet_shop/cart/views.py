# cart/views.py
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Cart, CartItem
from products.models import Product, Category
from .forms import AddToCartForm
from django.contrib.auth.decorators import login_required

def get_cart(request):
    """Получаем корзину: у юзера или по сессии"""
    if request.user.is_authenticated:
        new_cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        new_cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return new_cart


def add_to_cart(request, product_id):

    new_product = get_object_or_404(Product, id=product_id)

    # --- 1. Попробуем взять quantity напрямую (случай product_list.html) ---
    raw_quantity = request.POST.get("quantity")

    if raw_quantity is not None:
        try:
            quantity = int(raw_quantity)
        except ValueError:
            messages.error(request, "Invalid quantity")
            quantity = 1 # fallback

    else:
        # --- 2. Если quantity нет, пробуем через форму (случай product_detail.html) ---
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
        else:
            messages.error(request, "Invalid quantity")
            return redirect("products:product_detail", product_id=product_id)

    # --- 3. Берём корзину ---
    current_cart = get_cart(request)

    # --- 4. Создаём или обновляем позицию ---

    cart_item, created = CartItem.objects.get_or_create(
        cart=current_cart,
        product=new_product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()


    messages.success(request, f"Added {quantity} × {new_product.name} to cart!")

    return redirect(request.META.get("HTTP_REFERER", "cart:cart_detail"))


  
def cart_detail(request):
    current_cart = get_cart(request)
    list_items = current_cart.items.all()

    cart_cost = current_cart.total_price
    cart_total_quantity = current_cart.total_items

    context = {
        'cart': current_cart,
        'list_items': list_items,
        'cart_cost': cart_cost,
        'cart_total_quantity': cart_total_quantity,
    }

    return render(request, 'cart/cart_detail.html', context)

def remove_from_cart(request, item_id):
    current_cart = get_cart(request)

    # достаём объект только из корзины текущего юзера/сессии
    item = get_object_or_404(CartItem, id=item_id, cart=current_cart)  

    item.delete()
    messages.info(request, f"{item.product.name} removed from cart")

    return redirect("cart:cart_detail")

