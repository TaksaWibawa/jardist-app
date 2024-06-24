from django.contrib import messages
from django.shortcuts import render, redirect
from jardist.forms.task_form import TaskForm
from jardist.models.task_models import Task

def CreateTaskPage(request):
    form = TaskForm(request=request)

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, request=request, is_create_page=True)

        if form.is_valid():
            task = form.save(commit=False)
            if task is not None:
                task.save()
                messages.success(request, 'Data berhasil disimpan')

                if 'save_and_continue' in request.POST:
                    return redirect('view_pk', pk_id=task.pk_instance.id)

                elif 'save_and_add_another' in request.POST:
                    return redirect('create_task')

            else:
                messages.error(request, 'Tidak ada sub pekerjaan pada file')

        else:
            messages.error(request, 'Data gagal disimpan')

    context = {'form': form}
    return render(request, 'pages/create_task_page.html', context)

def EditTaskPage(request, task_id):
    task = Task.objects.get(id=task_id)
    form = TaskForm(request.POST or None, request.FILES or None, instance=task, request=request, is_create_page=False)

    if request.method == 'POST':
        if form.is_valid():
            if task is not None:
                form.save()
                messages.success(request, 'Data berhasil disimpan')
                return redirect('view_pk', pk_id=task.pk_instance.id)
            else:
                messages.error(request, 'Tidak ada sub pekerjaan pada file')
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form, 'task': task}

    return render(request, 'pages/edit_task_page.html', context)