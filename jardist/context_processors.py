def navigations(request):
    NAV_ITEMS = [
        {"name": "REGISTER SPK", "url": "create_spk"},
        {"name": "REGISTER PK", "url": "home"},
        {"name": "REGISTER PEKERJAAN", "url": "home"},
        {"name": "LIST PK", "url": "home"},
        {"name": "REGISTER ARSIP DOKUMEN", "url": "home"},
        {"name": "REGISTER DOKUMENTASI PEKERJAAN", "url": "home"},
        {"name": "VIEW ARSIP DOKUMEN", "url": "home"},
        {"name": "VIEW DOKUMENTASI PEKERJAAN", "url": "home"}
    ]

    return { "NAV_ITEMS": NAV_ITEMS }