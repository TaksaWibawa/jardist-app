from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from jardist.forms.archive_form import DocumentFormSet, PKSelectForm
from jardist.forms.bast_form import BASTForm, UpdateTaskStatusFormset
from jardist.forms.pk_form import PKForm
from jardist.models.contract_models import SPK, PK, PKArchiveDocument
from jardist.models.task_models import Task
from jardist.services.task_service import get_sub_tasks_materials_by_category
from jardist.decorators import login_and_group_required

@login_and_group_required('Staff')
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

@login_and_group_required('Staff')
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

@login_and_group_required('Staff')
def UpdateBASTPage(request, pk_id):
    pk = PK.objects.get(id=pk_id)
    tasks = Task.objects.filter(pk_instance=pk).order_by('id')
    form = BASTForm(request.POST or None, instance=pk)

    formset = UpdateTaskStatusFormset(request.POST or None, queryset=tasks, prefix='task')

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_pk', pk_id=pk_id)
        else:
            messages.error(request, 'Data gagal disimpan')
        
    tasks_and_forms = list(zip(tasks, formset.forms))
    context = {'form': form, 'pk': pk, 'tasks_and_forms': tasks_and_forms, 'formset': formset, 'tasks': tasks}

    return render(request, 'pages/update_bast_page.html', context)

@login_and_group_required()
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

@login_and_group_required()
def ListPKPage(request):
    status_mapping = {
        'ktk_done': 'PEMBAYARAN',
        'payment': 'PEMELIHARAAN',
        'pk_done': 'SELESAI',
    }

    if request.method == 'POST':
        pk_number = request.POST.get('pk_number')
        action = request.POST.get('action')
        
        new_status = status_mapping.get(action)
        
        if new_status:
            try:
                pk = PK.objects.get(pk_number=pk_number)
                pk.status = new_status
                pk.save()
                return HttpResponseRedirect(reverse('list_pk'))
            except PK.DoesNotExist:
                pass

    spks = SPK.objects.all().order_by('id')
    selected_spk = request.GET.get('spk')

    if selected_spk:
        pks = PK.objects.prefetch_related('tasks').filter(spk__spk_number=selected_spk).order_by('pk_number')
    else:
        pks = PK.objects.prefetch_related('tasks').all().order_by('pk_number')

    context = {'pks': pks, 'spks': spks, 'selected_spk': selected_spk}
    return render(request, 'pages/list_pk_page.html', context)

@login_and_group_required('Staff', 'Pengawas')
def CreateArchiveDocumentPage(request):
    pk_number = request.GET.get('pk')
    pk_instance = PK.objects.get(pk_number=pk_number) if pk_number else None
    form = PKSelectForm(request.POST or None, initial={'pk_instance': pk_instance})
    formset = DocumentFormSet(request.POST or None, request.FILES or None, prefix='document')
    first_formset_empty = False


    if request.method == 'POST' and form.is_valid():
        pk_archive_instance = PKArchiveDocument(pk_instance=form.cleaned_data['pk_instance'])
        first_form = formset.forms[0]
        if formset.is_valid():
            if not first_form.cleaned_data.get('pickup_file'):
                messages.error(request, 'Isi Field Pertama!')
                first_formset_empty = True
            else:
                pk_archive_instance.save()
                formset.instance = pk_archive_instance
                formset.save()
                messages.success(request, 'Data berhasil disimpan')
                return HttpResponseRedirect(reverse('view_archive_document') + '?pk=' + str(pk_archive_instance.pk_instance.pk_number))
        else:
            messages.error(request, 'Data gagal disimpan')

    context = {'form': form, 'formset': formset, 'first_formset_empty': first_formset_empty}
    return render(request, 'pages/create_archive_page.html', context)

@login_and_group_required('Staff', 'Pengawas', 'Direktur')
def ViewArchiveDocumentPage(request):
    pks = PK.objects.all().order_by('pk_number')
    pk_number = request.GET.get('pk')
    documents_with_dates = [] 
    pk = None

    if pk_number:
        try:
            pk = PK.objects.get(pk_number=pk_number)
            pk_archive_instances = PKArchiveDocument.objects.filter(pk_instance=pk).annotate(doc_count=Count('documents')).order_by('-id')
            for pk_archive_instance in pk_archive_instances:
                for document in pk_archive_instance.documents.all():
                    documents_with_dates.append((document, pk_archive_instance.created_at))
        except PK.DoesNotExist:
            messages.error(request, 'Data tidak ditemukan')
    else:
        pk_archive_instances = PKArchiveDocument.objects.annotate(doc_count=Count('documents')).order_by('-doc_count')
        for pk_archive_instance in pk_archive_instances:
            for document in pk_archive_instance.documents.all():
                documents_with_dates.append((document, pk_archive_instance.created_at))

    context = {'pks': pks, 'documents_with_dates': documents_with_dates, 'pk': pk, 'selected_pk_number': pk_number}
    return render(request, 'pages/view_archive_page.html', context)