# account/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib import messages
#from django.contrib.sessions.models import Session

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('blogg:index')
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})


def register_view(request):    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save() # Сохраняет пользователя с хэшированным паролем
            login(request, user) # Автоматически входим после регистрации
            messages.success(request, f"Welcome, {user.username}! you successfully sighned up")
            return redirect('blogg:index')
    else:
        form = SignUpForm()
    return render(request, 'account/register.html', {'form': form})

