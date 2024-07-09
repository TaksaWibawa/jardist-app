def navigations(request):
    user = request.user
    NAV_ITEMS = [
        {
            "name": "HOME",
            "url": "list_pk",
        },
        {
            "name": "TAMBAH DATA",
            "sub_items": [
                {"name": "REGISTER SPK", "url": "create_spk"},
                {"name": "REGISTER PK", "url": "create_pk"},
                {"name": "REGISTER PEKERJAAN", "url": "create_task"},
                {"name": "REGISTER ARSIP DOKUMEN", "url": "create_archive_document"},
                {"name": "REGISTER DOKUMENTASI PEKERJAAN", "url": "create_documentation"},
            ],
        },
        {
            "name": "LIHAT DATA",
            "sub_items": [
                {"name": "VIEW ARSIP DOKUMEN", "url": "view_archive_document"},
                {"name": "VIEW DOKUMENTASI PEKERJAAN", "url": "view_documentation"},
            ],
        },
    ]

    # Filter NAV_ITEMS based on user group
    if user.groups.filter(name='Direktur').exists():
        NAV_ITEMS = [item for item in NAV_ITEMS if item['name'] == 'LIHAT DATA']
    elif user.groups.filter(name='Pengawas').exists():
        allowed_urls = ['list_pk', 'create_archive_document', 'create_documentation', 'view_archive_document', 'view_documentation']
        NAV_ITEMS = [item for item in NAV_ITEMS if item.get('url') in allowed_urls or any(sub_item['url'] in allowed_urls for sub_item in item.get('sub_items', []))]
        for item in NAV_ITEMS:
            if 'sub_items' in item:
                item['sub_items'] = [sub_item for sub_item in item['sub_items'] if sub_item['url'] in allowed_urls]

    current_url_name = request.resolver_match.url_name
    for item in NAV_ITEMS:
        item['open_accordion'] = False
        item['is_active'] = item.get('url') == current_url_name
        if 'sub_items' in item:
            for sub_item in item['sub_items']:
                sub_item['is_active'] = sub_item['url'] == current_url_name
                if sub_item['is_active']:
                    item['open_accordion'] = True

    return {"NAV_ITEMS": NAV_ITEMS}