from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, redirect
from jardist.forms.pk_form import PKForm
from jardist.models.contract_models import SPK, PK
from jardist.models.task_models import Task

def CreatePKPage(request):
    spk_id = request.GET.get('spk_id', None)
    is_create_page = True

    try:
        spk = SPK.objects.get(id=spk_id)
        if spk.is_without_pk:
            is_create_page = False
    except SPK.DoesNotExist:
        pass

    form = PKForm(request.POST or None, spk_id=spk_id, is_create_page=is_create_page)

    if request.method == 'POST':
        if form.is_valid():
            pk = form.save(commit=False)
            if hasattr(request.user, 'userprofile'):
                pk.department = request.user.userprofile.department
            pk.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('create_task')
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form}

    return render(request, 'pages/create_pk_page.html', context)

def EditPKPage(request, pk_id):
    pk = PK.objects.get(id=pk_id)
    form = PKForm(request.POST or None, instance=pk, is_create_page=False)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_pk', pk_id=pk_id)
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form, 'pk': pk}

    return render(request, 'pages/edit_pk_page.html', context)

def ViewPKPage(request, pk_id):
    pk = PK.objects.get(id=pk_id)
    tasks = Task.objects.filter(pk_instance=pk).prefetch_related('subtask_set__materials').order_by('id')

    paginator = Paginator(tasks, 1)

    page = request.GET.get('page')

    try:
        tasks_page = paginator.page(page)
    except PageNotAnInteger:
        tasks_page = paginator.page(1)
    except EmptyPage:
        tasks_page = paginator.page(paginator.num_pages)

    tasks_page_data = []
    for task in tasks_page:
        sub_tasks_materials_by_category = {}
        sub_tasks = list(task.subtask_set.all())

        for sub_task in sub_tasks:
            materials_by_category = {}
            for sub_task_material in sub_task.subtaskmaterial_set.all():
                material = sub_task_material.material
                material.client_volume = sub_task_material.client_volume
                material.contractor_volume = sub_task_material.contractor_volume
                materials_by_category.setdefault(material.category, []).append(material)
            sub_tasks_materials_by_category[sub_task] = materials_by_category

        tasks_page_data.append({
            'task': task,
            'sub_tasks_materials_by_category': sub_tasks_materials_by_category,
        })

    context = {'pk': pk, 'tasks_page_data': tasks_page_data, 'tasks_page': tasks_page}
    return render(request, 'pages/view_pk_page.html', context)

def check_pk_in_spk(request, **kwargs):
    spk_id = kwargs.get('spk_id')
    try:
        spk = SPK.objects.get(id=spk_id)
        data = {
            'is_without_pk': spk.is_without_pk,
            'spk': spk.spk_number,
            'start_date': spk.start_date,
            'end_date': spk.end_date,
            'execution_time': spk.execution_time,
            'maintenance_time': spk.maintenance_time
        }
        return JsonResponse(data)
    except SPK.DoesNotExist:
        messages.error(request, 'SPK not found')
        return JsonResponse({'error': 'SPK not found'}, status=404)
    
def get_pk_data(request):
    pk_id = request.GET.get('pk_id')
    field = request.GET.get('field', 'execution_time')

    try:
        pk = PK.objects.get(id=pk_id)
        if hasattr(pk, field):
            return JsonResponse({field: getattr(pk, field)})
        else:
            return JsonResponse({'error': f'Field {field} not found'}, status=400)
    except PK.DoesNotExist:
        return JsonResponse({'error': 'PK not found'}, status=404)