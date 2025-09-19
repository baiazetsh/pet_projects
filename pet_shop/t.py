

 action="{% url 'orders:order_review' order.id %}"




@login_required
def order_pay(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)

    if order.status == "paid":
        messages.info(request, "Order has already paid")
        
        return render(request, "orders/order_detail.html", {"order": order})
    
    if request.method == 'POST':
        # форма ввода платежа здесь
        order.status = "paid"
        cart.checked_out = True
        cart.save()            
        messages.success(request, "Paid succesfully")

        return redirect('orders:order_detail', order_id=order.id)

   # return render(request, "orders/order_detail.html", {"order": order})
