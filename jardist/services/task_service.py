from itertools import groupby
from jardist.models.task_models import SubTaskMaterial
from jardist.forms.sub_task_material_form import SubTaskMaterialFormSet

def get_sub_tasks_materials_by_category(task, sort_by='rab', search=''):
    sub_tasks_materials_by_category = {}
    sub_task_materials = SubTaskMaterial.objects.filter(subtask__task=task, material__name__icontains=search).order_by('subtask').select_related('subtask', 'material', 'category')
    sub_task_materials_by_sub_task = {sub_task: list(stms) for sub_task, stms in groupby(sub_task_materials, key=lambda x: x.subtask)}

    for sub_task, stms in sub_task_materials_by_sub_task.items():
        materials_by_category = {}
        for stm in stms:
            material = stm.material
            if sort_by == 'realization':
                material.client_volume = stm.realization_client_volume
                material.contractor_volume = stm.realization_contractor_volume
            else:
                material.client_volume = stm.rab_client_volume
                material.contractor_volume = stm.rab_contractor_volume
            materials_by_category.setdefault(stm.category, []).append(material)

        sorted_materials_by_category = {}
        for category in sorted(materials_by_category.keys(), key=lambda x: 0 if x.name == 'Material Utama' else 1 if x.name == 'Material Non Utama' else 2 if x.name == 'Lain - Lain' else 3):
            sorted_materials = sorted(materials_by_category[category], key=lambda x: (-x.client_volume if x.client_volume is not None else 0, -x.contractor_volume if x.contractor_volume is not None else 0, x.name))
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