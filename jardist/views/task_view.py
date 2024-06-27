from django.contrib import messages
from django.shortcuts import render, redirect
from jardist.forms.realization_task_form import RealizationTaskForm
from jardist.forms.task_form import TaskForm
from jardist.models.task_models import Task
from jardist.services.task_service import create_subtask_material_formsets

def CreateTaskPage(request):
    pk_id = request.GET.get('pk_id', None)
    form = TaskForm(request.POST or None, request.FILES or None, request=request, is_create_page=True, pk_id=pk_id)

    if request.method == 'POST':
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
                messages.error(request, 'Data gagal disimpan')
        else:
            messages.error(request, 'Data gagal disimpan')

    context = {'form': form}
    return render(request, 'pages/create_task_page.html', context)

def EditTaskPage(request, task_id):
    task = Task.objects.get(id=task_id)
    form = TaskForm(request.POST or None, request.FILES or None, instance=task, request=request, is_create_page=False)

    if request.method == 'POST':
        if form.is_valid():
            task = form.save(commit=False)
            if task is not None:
                task.save()
                messages.success(request, 'Data berhasil disimpan')
                return redirect('view_pk', pk_id=task.pk_instance.id)
            else:
                messages.error(request, 'Data gagal disimpan')
        else:
            messages.error(request, 'Data gagal disimpan')

    context = {'form': form, 'task': task}
    return render(request, 'pages/edit_task_page.html', context)

def EditTaskMaterialPage(request, task_id):
    task = Task.objects.get(id=task_id)
    formsets, formsets_data = create_subtask_material_formsets(request, task, sort_by='rab')

    if request.method == 'POST':
        if all(formset.is_valid() for material, formset in formsets_data):
            for material, formset in formsets_data:
                formset.save()
            
            messages.success(request, 'Data berhasil disimpan')
            return redirect('edit_task', task_id=task.id)
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'formsets': formsets, 'task': task}

    return render(request, 'pages/edit_task_material_page.html', context)

def UpdateRealizationTaskPage(request, task_id):
    task = Task.objects.get(id=task_id)
    form = RealizationTaskForm(request.POST or None, instance=task)

    if request.method == 'POST':
        if form.is_valid():
            if form.has_changed():
                task = form.save(commit=False)
                task.save()

            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_pk', pk_id=task.pk_instance.id)
        else:
            messages.error(request, 'Data gagal disimpan')

    context = {'form': form, 'task': task}
    return render(request, 'pages/update_realization_task_page.html', context)

def UpdateRealizationTaskMaterialPage(request, task_id):
    task = Task.objects.get(id=task_id)
    formsets, formsets_data = create_subtask_material_formsets(request, task, sort_by='realization')

    if request.method == 'POST':
        if all(formset.is_valid() for material, formset in formsets_data):
            for material, formset in formsets_data:
                formset.save()

            messages.success(request, 'Data berhasil disimpan')
            return redirect('update_realization_task', task_id=task.id)
        else:
            messages.error(request, 'Data gagal disimpan')

    context = {'formsets': formsets, 'task': task}
    return render(request, 'pages/update_realization_task_material_page.html', context)


