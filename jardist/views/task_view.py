from django.contrib import messages
from django.shortcuts import render, redirect
from jardist.forms.realization_task_form import RealizationTaskForm
from jardist.forms.sub_task_material_form import SubTaskMaterialFormSet
from jardist.forms.task_form import TaskForm
from jardist.models.task_models import Task, SubTaskMaterial
from jardist.services.task_service import get_sub_tasks_materials_by_category

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
    search = request.GET.get('search', '')

    sub_tasks_materials_by_category = get_sub_tasks_materials_by_category(task, sort_by='rab', search=search)
    formsets = {}
    formsets_data = []

    for sub_task, materials_by_category in sub_tasks_materials_by_category.items():
        formsets[sub_task] = {}
        for category, materials in materials_by_category.items():
            material_formsets = []
            for material in materials:
                queryset = SubTaskMaterial.objects.filter(subtask=sub_task, material=material)
                formset_initial_data = [
                    {
                        'rab_client_volume': stm.rab_client_volume if stm.rab_client_volume is not None else 0,
                        'rab_contractor_volume': stm.rab_contractor_volume if stm.rab_contractor_volume is not None else 0
                    } 
                    for stm in queryset
                ]
                formset = SubTaskMaterialFormSet(
                    request.POST or None,
                    queryset=queryset,
                    initial=formset_initial_data,
                    prefix=f'{sub_task}_{category}_{material.id}'
                )
                material_formsets.append((material, formset))
            
            formsets[sub_task][category] = material_formsets
            formsets_data.extend(material_formsets)

    if request.method == 'POST':
        if all(formset.is_valid() for material, formset in formsets_data):
            for material, formset in formsets_data:
                formset.save()
            
            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_pk', pk_id=task.pk_instance.id)
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
    search = request.GET.get('search', '')

    sub_tasks_materials_by_category = get_sub_tasks_materials_by_category(task, sort_by='realization', search=search)
    formsets = {}
    formsets_data = []

    for sub_task, materials_by_category in sub_tasks_materials_by_category.items():
        formsets[sub_task] = {}
        for category, materials in materials_by_category.items():
            material_formsets = []
            for material in materials:
                queryset = SubTaskMaterial.objects.filter(subtask=sub_task, material=material)
                formset_initial_data = [
                    {
                        'realization_client_volume': stm.realization_client_volume if stm.realization_client_volume is not None else stm.rab_client_volume or 0,
                        'realization_contractor_volume': stm.realization_contractor_volume if stm.realization_contractor_volume is not None else stm.rab_contractor_volume or 0
                    } 
                    for stm in queryset
                ]
                formset = SubTaskMaterialFormSet(
                    request.POST or None,
                    queryset=queryset,
                    initial=formset_initial_data,
                    show_type='realization',
                    prefix=f'{sub_task}_{category}_{material.id}'
                )
                material_formsets.append((material, formset))
            
            formsets[sub_task][category] = material_formsets
            formsets_data.extend(material_formsets)

    if request.method == 'POST':
        if all(formset.is_valid() for material, formset in formsets_data):
            for material, formset in formsets_data:
                formset.save()

            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_pk', pk_id=task.pk_instance.id)
        else:
            messages.error(request, 'Data gagal disimpan')

    context = {'formsets': formsets, 'task': task}
    return render(request, 'pages/update_realization_task_material_page.html', context)


