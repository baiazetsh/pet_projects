#users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False,
        widget=forms.EmailInput(
                attrs={'placeholder': "Email (optional)"})
    ),

    class Meta:
        model =User
        fields = ["username", "email", 'password1', "password2"]
