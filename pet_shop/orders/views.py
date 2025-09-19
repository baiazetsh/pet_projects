#orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.views import get_cart       #cart/views.py
from .models import Order, OrderItem
from cart.forms import CheckoutForm


@login_required
def checkout(request):
    # Получаем корзину для юзера или сессии
    current_cart = get_cart(request)
    if not current_cart.items.exists():
        messages.warning(request, "Your cart is empty")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # makig order
            new_order = Order.objects.create(
                user=request.user, #if request.user.is_authenticated else None,
                shipping_address=form.cleaned_data['shipping_address'],
           
                billing_address=form.cleaned_data['billing_address'],
                payment_method=form.cleaned_data['payment_method'],
                total_price=current_cart.total_price,
                notes=form.cleaned_data.get('notes', ''),
                status="draft"
            )
            # Переносим товары из корзины в заказ
            for cart_item in current_cart.items.all():
                OrderItem.objects.create(
                    order=new_order,
                    product=cart_item.product,
                    name=cart_item.product.name,
                    price=cart_item.product.current_price,
                    quantity=cart_item.quantity,
                    total_price=cart_item.total_price
                )
            # clear cart after checkout
            #current_cart.items.all().delete()
            #messages.success(request, f"Order #{new_order.id} created succesfully")
            
            return redirect('orders:order_review', id=new_order.id)

    else:
        form = CheckoutForm()

    return render(request, 'orders/checkout.html', {'form': form, 'cart': current_cart})

@login_required
def order_detail(request, order_id):
    # getting current order
    current_order = get_object_or_404(Order, id=order_id, user=request.user)

    # all items in the cart
    order_items = current_order.items.all()
    current_status = "pending"

    context = {
        "order": current_order,
        "orders_items": order_items.all(),
        "status": current_status,
    }
    return render(request, "orders/order_detail.html", context)


@login_required
def order_review(request, id):
    review_order = get_object_or_404(Order, id=id, user=request.user)
    if request.method == 'POST':
        # confirm order
        #review_order.status = "pending"
       # review_order.save()

        # erase a cart now
        #cart = get_cart(request)
        #cart.items.all().delete()
        return redirect("orders:order_pay", id=review_order.id)

    #messages.success(request, f"Order #{review_order.id} confirmed and cart cleared")
    return render(request, "orders/order_review.html", {"order": review_order, "items": review_order.items.all()})
  
@login_required
def order_pay(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    order.status = "paid"
    order.save()
    cart = get_cart(request)
    cart.checked_out = True
    cart.save()
    return redirect("orders:order_detail", order_id=order.id)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)

    return render(request, "orders/order_list.html", {"orders": orders})