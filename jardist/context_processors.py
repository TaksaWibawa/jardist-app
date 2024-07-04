def navigations(request):
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
                {"name": "REGISTER DOKUMENTASI PEKERJAAN", "url": "create_archive_document"},
            ],
        },
        {
            "name": "LIHAT DATA",
            "sub_items": [
                {"name": "VIEW ARSIP DOKUMEN", "url": "view_archive_document"},
                {"name": "VIEW DOKUMENTASI PEKERJAAN", "url": "view_archive_document"},
            ],
        },
    ]

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