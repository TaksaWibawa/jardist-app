from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from itertools import groupby
from jardist.forms.material_form import MaterialForm
from jardist.forms.sub_task_material_form import SubTaskMaterialFormSet
from jardist.models.task_models import SubTaskMaterial
from jardist.models.task_models import Task

def add_material(request, task_id, redirect_url, context='rab'):
    task = Task.objects.get(id=task_id)
    material_form = MaterialForm(request.POST or None, task=task, context=context)

    if request.method == 'POST':
        if material_form.is_valid():
            material_form.save()
            messages.success(request, 'Data berhasil disimpan')
            return JsonResponse({'error': False})
        else:
            form_errors = material_form.errors.as_json()
            return JsonResponse({'error': True, 'form_errors': form_errors})
    return redirect(redirect_url, task_id=task.id)

def AddRABMaterial(request, task_id):
    return add_material(request, task_id, 'edit_task_material', 'rab')

def AddRealizationMaterial(request, task_id):
    return add_material(request, task_id, 'update_realization_task_material', 'realization')

def get_sub_tasks_materials_by_category(task, sort_by='', search=''):
    sub_tasks_materials_by_category = {}
    sub_task_materials = SubTaskMaterial.objects.filter(subtask__task=task, material__name__icontains=search).order_by('-subtask').select_related('subtask', 'material', 'category')
    sub_task_materials_by_sub_task = {sub_task: list(stms) for sub_task, stms in groupby(sub_task_materials, key=lambda x: x.subtask)}

    def has_volume_changed(current_client_volume, previous_client_volume, current_contractor_volume, previous_contractor_volume):
        return current_client_volume != previous_client_volume or current_contractor_volume != previous_contractor_volume

    for sub_task, stms in sub_task_materials_by_sub_task.items():
        materials_by_category = {}
        for stm in stms:
            material = stm.material

            if sort_by == 'realization':
                material.client_volume = stm.realization_client_volume
                material.contractor_volume = stm.realization_contractor_volume
            elif sort_by == 'rab':
                material.client_volume = stm.rab_client_volume
                material.contractor_volume = stm.rab_contractor_volume
            else:
                material.rab_client_volume = stm.rab_client_volume
                material.rab_contractor_volume = stm.rab_contractor_volume
                material.realization_client_volume = stm.realization_client_volume
                material.realization_contractor_volume = stm.realization_contractor_volume

            material.has_volume_changed = has_volume_changed(stm.realization_client_volume, stm.rab_client_volume, stm.realization_contractor_volume, stm.rab_contractor_volume)

            material.labor_price = stm.labor_price or 0
            material.category = stm.category
            material.price = stm.material_price or 0
            material.is_additional = stm.is_additional
            materials_by_category.setdefault(stm.category, []).append(material)

        sorted_materials_by_category = {}
        if sort_by in ['rab', 'realization']:
            for category in sorted(materials_by_category.keys(), key=lambda x: 0 if x.name == 'Material Utama' else 1 if x.name == 'Material Non Utama' else 2 if x.name == 'Lain - Lain' else 3):
                sorted_materials = sorted(materials_by_category[category], key=lambda x: (-x.client_volume if x.client_volume is not None else 0, -x.contractor_volume if x.contractor_volume is not None else 0, x.name))
                sorted_materials_by_category[category] = sorted_materials
        else:
            for category in sorted(materials_by_category.keys(), key=lambda x: 0 if x.name == 'Material Utama' else 1 if x.name == 'Material Non Utama' else 2 if x.name == 'Lain - Lain' else 3):
                for material in materials_by_category[category]:
                    material.combined_volume = material.rab_client_volume or 0 + material.rab_contractor_volume or 0 + material.realization_client_volume or 0 + material.realization_contractor_volume or 0
                
                sorted_materials = sorted(materials_by_category[category], key=lambda x: (-x.combined_volume, x.name))
                sorted_materials_by_category[category] = sorted_materials

        sub_tasks_materials_by_category[sub_task] = sorted_materials_by_category

    return sub_tasks_materials_by_category

def create_subtask_material_formsets(request, task, sort_by):
    search = request.GET.get('search', '')
    sub_tasks_materials_by_category = get_sub_tasks_materials_by_category(task, sort_by=sort_by, search=search)
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
                        f'{sort_by}_client_volume': getattr(stm, f'{sort_by}_client_volume', stm.rab_client_volume) or 0,
                        f'{sort_by}_contractor_volume': getattr(stm, f'{sort_by}_contractor_volume', stm.rab_contractor_volume) or 0
                    } 
                    for stm in queryset
                ]
                formset = SubTaskMaterialFormSet(
                    request.POST or None,
                    queryset=queryset,
                    initial=formset_initial_data,
                    show_type=sort_by,
                    prefix=f'{sub_task}_{category}_{material.id}'
                )
                material_formsets.append((material, formset))
            
            formsets[sub_task][category] = material_formsets
            formsets_data.extend(material_formsets)

    return formsets, formsets_data

def get_task_data(request):
    pk = request.GET.get('pk')
    tasks = Task.objects.filter(pk_instance=pk).values('id', 'task_name')
    return JsonResponse(list(tasks), safe=False)