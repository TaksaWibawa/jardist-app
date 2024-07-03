import zipfile
import requests
import os
import math
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
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

    response = HttpResponse(content_type='application/zip')
    zf = zipfile.ZipFile(response, 'w')

    for url in urls:
        print(f"Fetching {url}")
        if url.startswith('/static/'):
            file_path = os.path.join(settings.BASE_DIR, url[1:])
            try:
                with open(file_path, 'rb') as file:
                    filename = os.path.basename(url)
                    zf.writestr(filename, file.read())
            except IOError:
                print(f"Failed to open {url}")
        else:
            res = requests.get(url)
            if res.status_code == 200:
                filename = os.path.basename(url)
                zf.writestr(filename, res.content)
            else:
                print(f"Failed to fetch {url}")

    zf.close()

    response['Content-Disposition'] = 'attachment; filename="all_documents.zip"'
    return response