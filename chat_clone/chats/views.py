#chats/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Chat, Message, Like
from .forms import ChatForm, MessageForm
from django.contrib import messages


def index(request):
    chat_list = Chat.objects.all()
   
    
    context = {
        'chat_list': chat_list,
    }
    return render(request, 'chats/index.html', context)

@login_required
def new_chat(request):
    if request.method  == "POST":
        form = ChatForm(request.POST, request.FILES)
        if form.is_valid():
            new_chat = form.save(commit=False)
            new_chat.author = request.user
            new_chat.save()
            form.save_m2m()
            messages.success(request, "Created successfully")

            return redirect('chats:chat_detail', chat_id=new_chat.id)
    else:
        form = ChatForm()

    return render(request,'chats/new_chat.html', {'form': form})

def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    chat_messages = chat.messages.all().order_by("created_at")

    context = {
        "chat": chat,
        "chat_messages": chat_messages,
        #"chat_id": chat.id,
    }
    return render(request, 'chats/chat_detail.html', context)


@login_required
def new_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.author = request.user
            message.save()
            return redirect("chats:chat_detail", chat_id=chat.id)
    else:
        form = MessageForm()

    context = {
        "form": form,
        "chat": chat,
    }
    return render(request, "chats/new_message.html", context)



@login_required
def toggle_like(request, message_id)    :
    return messages.info(request, "Лайки пока не реализованы")