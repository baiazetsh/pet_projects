#account/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    '''
    Создаём форму регистрации
    Наследуемся от UserCreationForm — 
    встроенной формы Django для создания пользователя.
    '''
    email = forms.EmailField(required=False, help_text='optional')

    class Meta:
        model = User
        # указываем, какие поля показывать.
        fields = ('username', 'email', 'password1', 'password2')
