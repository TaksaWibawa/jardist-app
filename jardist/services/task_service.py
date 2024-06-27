from itertools import groupby
from jardist.models.task_models import SubTaskMaterial

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
        for category in sorted(materials_by_category.keys(), key=lambda x: 0 if x.name == 'Material Utama' else 1 if x.name == 'Material Non Utama' else 2):
            sorted_materials = sorted(materials_by_category[category], key=lambda x: (-x.client_volume if x.client_volume is not None else 0, -x.contractor_volume if x.contractor_volume is not None else 0, x.name))
            sorted_materials_by_category[category] = sorted_materials

        sub_tasks_materials_by_category[sub_task] = sorted_materials_by_category

    return sub_tasks_materials_by_category