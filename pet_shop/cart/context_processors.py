# context_processors.py
from cart.models import Cart

def cart(request):

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        cart = None
    return {"cart": cart}