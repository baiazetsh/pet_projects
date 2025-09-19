#users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib import messages
from .models import UserProfile

def login_view(request):
    if request.method == "POST":
        form =AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user =form.get_user()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")

            return redirect('chats:index')
    else:
        form =AuthenticationForm()

    return render(request, "users/login.html", {"form": form})
            

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! you successfully sighned up")

            return redirect('chats:index')

    else:
        form = SignUpForm()
    
    messages.warning(request, "Singup or login please")
    return render(request, 'users/register.html', {'form': form})



def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("chats:index")

