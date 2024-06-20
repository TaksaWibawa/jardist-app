from django.contrib import messages
from django.shortcuts import render, redirect
from jardist.forms.task_form import TaskForm

def CreateTaskPage(request):
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            messages.success(request, 'Data berhasil disimpan')

            if 'save_and_continue' in request.POST:
                return redirect('home')
            elif 'save_and_add_another' in request.POST:
                return redirect('create_task')
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form}

    return render(request, 'pages/create_task_page.html', context)