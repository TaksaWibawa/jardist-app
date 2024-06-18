from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from jardist.forms.pk_form import PKForm
from jardist.models import SPK

def CreatePKPage(request):
    form = PKForm(is_create_page=True)

    if request.method == 'POST':
        form = PKForm(request.POST, is_create_page=True)
        if form.is_valid():
            pk = form.save(commit=False)
            if hasattr(request.user, 'userprofile'):
                pk.department = request.user.userprofile.department
            pk.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('home')
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form}

    return render(request, 'pages/create_pk_page.html', context)

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