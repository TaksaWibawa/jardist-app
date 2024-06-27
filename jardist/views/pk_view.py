from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from jardist.forms.pk_form import PKForm
from jardist.forms.bast_form import BASTForm
from jardist.models.contract_models import SPK, PK
from jardist.models.task_models import Task
from jardist.services.task_service import get_sub_tasks_materials_by_category

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
            return HttpResponseRedirect(reverse('create_task') + '?pk_id=' + str(pk.id))
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

def UpdateBASTPage(request, pk_id):
    pk = PK.objects.get(id=pk_id)
    form = BASTForm(request.POST or None, instance=pk)
    tasks = Task.objects.filter(pk_instance=pk).order_by('id')

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_pk', pk_id=pk_id)
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form, 'pk': pk, 'tasks': tasks}

    return render(request, 'pages/update_bast_page.html', context)

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
        sub_tasks_materials_by_category = get_sub_tasks_materials_by_category(task)
        tasks_page_data.append({
            'task': task,
            'sub_tasks_materials_by_category': sub_tasks_materials_by_category,
        })

    context = {'pk': pk, 'tasks_page_data': tasks_page_data, 'tasks_page': tasks_page}
    return render(request, 'pages/view_pk_page.html', context)