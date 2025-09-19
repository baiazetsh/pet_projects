#managerr/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from django.contrib import messages


        # показывает все задачи текущего пользователя.
@login_required
def task_list(request):
    # фильтр из URL: ?filter=active / ?filter=completed / ?filter=all
    current_filter =request.GET.get("filter", "all")

    tasks = Task.objects.filter(owner=request.user).order_by('-created_at')

    if current_filter == "active":
        tasks = tasks.filter(status=False)
    elif current_filter == "completed":
        tasks = tasks.filter(status=True)
    # "all" или неизвестный фильтр → ничего не меняем
    context = {
        'tasks': tasks,
        "current_filter": current_filter,
    }
    return render(request, 'managerr/task_list.html', context)


    # форма + обработка POST.
@login_required
def task_new(request):
    if request.method != 'POST': 
        form = TaskForm()
    else:
        form =TaskForm(request.POST, request.FILES) 
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            messages.success(request, "The task has been created")
            return redirect("managerr:task_list")

    context = {
        'form': form,
    }
    return render(request, 'managerr/task_form.html', context)


    # доступно только владельцу задачи.
@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if task.owner != request.user:
        messages.error(request, "You aren't the owner of this task")
        return redirect('managerr:task_list')

    if request.method == 'POST':
        form = TaskForm(instance=task, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "The task has been edited")
            return redirect('managerr:task_list')
    else:
        form = TaskForm(instance=task)
    context = {
        'form': form,
        'task': task,
    }
    return render(request, 'managerr/task_form.html', context)


        # подтверждение и удаление.
@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method == 'POST':
        task.delete()
        messages.success(request, "The task has been deleted")
        return redirect('managerr:task_list')

    context = {
        'task': task,
    }
    return render(request, 'managerr/task_confirm_delete.html', context)


        #подробная страница задачи.
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    context = {
        "task": task,
    }
    return render(request, "managerr/task_detail.html", context)  