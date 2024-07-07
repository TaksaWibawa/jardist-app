import zipfile
import requests
import os
import math
import json
import io
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings

def clean_decimal_field(value):
    if value in [None, ''] or (isinstance(value, float) and math.isnan(value)):
        return 0.0
    elif isinstance(value, str):
        return float(value.replace(',', ''))
    else:
        return float(value)

@csrf_exempt
@require_POST
def download_all_documents(request):
    data = json.loads(request.body)
    urls = data.get('urls', [])

    zip_buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for url in urls:
                print(f"Fetching {url}")
                if url.startswith('/media/'):
                    file_path = os.path.join(settings.BASE_DIR, url[1:])
                    try:
                        with open(file_path, 'rb') as file:
                            filename = os.path.basename(url)
                            zf.writestr(filename, file.read())
                    except IOError as e:
                        print(f"Failed to open {url}. Error: {e}")
                        continue
                else:
                    try:
                        res = requests.get(url)
                        if res.status_code == 200:
                            filename = os.path.basename(url)
                            zf.writestr(filename, res.content)
                        else:
                            print(f"Failed to fetch {url}. Status code: {res.status_code}")
                            continue
                    except requests.RequestException as e:
                        print(f"Request failed for {url}. Error: {e}")
                        continue

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="documents.zip"'

        return response
    except Exception as e:
        return JsonResponse({'error': f'Failed to create ZIP file. Error: {e}'}, status=500)
    finally:
        zip_buffer.close()