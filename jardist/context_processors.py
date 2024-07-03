def navigations(request):
    NAV_ITEMS = [
        {"name": "REGISTER SPK", "url": "create_spk"},
        {"name": "REGISTER PK", "url": "create_pk"},
        {"name": "REGISTER PEKERJAAN", "url": "create_task"},
        {"name": "LIST PK", "url": "list_pk"},
        {"name": "REGISTER ARSIP DOKUMEN", "url": "create_archive_document"},
        {"name": "REGISTER DOKUMENTASI PEKERJAAN", "url": "home"},
        {"name": "VIEW ARSIP DOKUMEN", "url": "view_archive_document"},
        {"name": "VIEW DOKUMENTASI PEKERJAAN", "url": "home"}
    ]

    return { "NAV_ITEMS": NAV_ITEMS }