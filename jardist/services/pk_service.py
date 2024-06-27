from django.http import JsonResponse
from django.contrib import messages
from jardist.models.contract_models import SPK, PK

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