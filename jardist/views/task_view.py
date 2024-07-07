from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from jardist.forms.documentation_form import TaskDocumentationForm, TaskDocumentationPhotoFormSet
from jardist.forms.material_form import MaterialForm
from jardist.forms.task_form import TaskForm
from jardist.models.contract_models import PK
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
                    return HttpResponseRedirect(reverse('create_task') + '?pk_id=' + str(pk_id))
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
    material_form = MaterialForm(request.POST or None, task=task, context='rab')

    if request.method == 'POST':
        if all(formset.is_valid() for material, formset in formsets_data):
            for material, formset in formsets_data:
                formset.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('edit_task', task_id=task.id)
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'formsets': formsets, 'task': task, 'material_form': material_form}

    return render(request, 'pages/edit_task_material_page.html', context)

def UpdateRealizationTaskMaterialPage(request, task_id):
    task = Task.objects.get(id=task_id)
    formsets, formsets_data = create_subtask_material_formsets(request, task, sort_by='realization')
    material_form = MaterialForm(request.POST or None, task=task, context='realization')

    if request.method == 'POST':
        if all(formset.is_valid() for material, formset in formsets_data):
            for material, formset in formsets_data:
                formset.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_pk', pk_id=task.pk_instance.id)
        else:
            messages.error(request, 'Data gagal disimpan')

    context = {'formsets': formsets, 'task': task, 'material_form': material_form}
    return render(request, 'pages/update_realization_task_material_page.html', context)

def CreateDocumentationPage(request):
    pk_id = request.GET.get('pk', None)
    pk_instance = PK.objects.get(id=pk_id) if pk_id else None
    form = TaskDocumentationForm(request.POST or None, initial={'pk_instance': pk_instance})
    formset = TaskDocumentationPhotoFormSet(request.POST or None, request.FILES or None, prefix='documentation')

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            task_documentation = form.save()
            formset.instance = task_documentation
            formset.save()

            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_documentation')
        else:
            messages.error(request, 'Data gagal disimpan')

    context = {
        'form': form,
        'formset': formset,
    }

    return render(request, 'pages/create_documentation_page.html', context)

def ViewDocumentationPage(request):
    pk_number = request.GET.get('pk')
    task_name = request.GET.get('task')
    tasks_with_documentations_and_photos = []
    pk = None
    pks = PK.objects.all().order_by('pk_number')
    all_tasks = Task.objects.all().order_by('task_name')

    if pk_number:
        try:
            pk = PK.objects.get(pk_number=pk_number)
            dropdown_tasks = Task.objects.filter(pk_instance=pk).order_by('task_name')
            tasks = dropdown_tasks.filter(task_name=task_name) if task_name else dropdown_tasks
        except PK.DoesNotExist:
            messages.error(request, 'Data tidak ditemukan')
            tasks = Task.objects.none()
            dropdown_tasks = Task.objects.none()
    else:
        tasks = all_tasks
        dropdown_tasks = all_tasks

    for task in tasks:
        documentations = task.documentations.all().order_by('created_at')
        for documentation in documentations:
            photos = documentation.photos.all().order_by('id')
            tasks_with_documentations_and_photos.append((task, documentation, photos))

    context = {
        'pks': pks,
        'tasks': dropdown_tasks,
        'tasks_with_documentations_and_photos': tasks_with_documentations_and_photos,
        'selected_pk_number': pk_number,
        'selected_task_name': task_name,
    }
    return render(request, 'pages/view_documentation_page.html', context)