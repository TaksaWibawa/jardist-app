from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from jardist.decorators import login_and_group_required
from jardist.forms.spk_form import SPKForm
from jardist.models.contract_models import SPK, PK

@login_and_group_required('Staff')
def CreateSPKPage(request):
    form = SPKForm()

    if request.method == 'POST':
        form = SPKForm(request.POST)
        if form.is_valid():
            spk = form.save(commit=False)
            if hasattr(request.user, 'userprofile'):
                spk.department = request.user.userprofile.department
            spk.save()
            messages.success(request, 'Data berhasil disimpan')

            if spk.is_without_pk:
                pk_id = PK.objects.get(spk=spk).id
                return HttpResponseRedirect(reverse('create_task') + '?pk_id=' + str(pk_id))
            else:
                return HttpResponseRedirect(reverse('create_pk') + '?spk_id=' + str(spk.id))
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form}

    return render(request, 'pages/create_spk_page.html', context)

@login_and_group_required('Staff')
def EditSPKPage(request, spk_id):
    spk = SPK.objects.get(id=spk_id)
    form = SPKForm(request.POST or None, instance=spk)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('view_spk', spk_id=spk_id)
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form, 'spk': spk}

    return render(request, 'pages/edit_spk_page.html', context)