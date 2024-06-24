from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from jardist.forms.spk_form import SPKForm
from jardist.models.contract_models import SPK
from urllib.parse import urlencode

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
                return redirect('create_task')
            else:
                base_url = reverse('create_pk')
                query_string = urlencode({'spk_id': spk.id})
                url = '{}?{}'.format(base_url, query_string)

                return redirect(url)
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form}

    return render(request, 'pages/create_spk_page.html', context)

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