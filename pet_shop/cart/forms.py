#CART/FORMS.PY
from django import forms

class AddToCartForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('paypal', 'PayPal'),
        ('cod', 'Cash on delivery'),
    ]

    payment_method = forms.ChoiceField(
        label="Способ оплаты",
        choices=PAYMENT_METHOD_CHOICES,
        initial='cod'
    )

    quantity = forms.IntegerField(
        min_value = 1,
        max_value=200,
        initial=1,
        widget = forms.NumberInput(attrs={'class': 'form-control'})
    )
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    
 
class CheckoutForm(forms.Form):

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Bank card'),
        ('paypal', 'PayPal'),
        ('cod', 'Cash on delivery'),
    ]

    payment_method = forms.ChoiceField(
        label="Payment method:*",
        choices=PAYMENT_METHOD_CHOICES,
        initial='cod'
    )

    shipping_address = forms.CharField(
        label="Delivery address*",
        widget=forms.Textarea(attrs={'rows': 3}),
        max_length=500,
        required=True
    )
    billing_address = forms.CharField(
        max_length=255,
        required=False
    )
    email = forms.EmailField(
        label="Email*",
        required=True
    )
    phone = forms.CharField(
        label="Phone",
        max_length=20,
        required=False
    )
    notes = forms.CharField(
        label="Comment to order",
        widget=forms.Textarea(attrs={'rows': 3}),
        max_length=1000,
        required=False
    )