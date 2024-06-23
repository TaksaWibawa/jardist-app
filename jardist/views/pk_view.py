from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from jardist.forms.pk_form import PKForm
from jardist.models.contract_models import SPK, PK

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