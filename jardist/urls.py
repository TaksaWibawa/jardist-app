from django.urls import path
from jardist.views import home_view, spk_view, pk_view, task_view

urlpatterns = [
  path('', home_view.HomePage, name='home'),

  path('spk/create/', spk_view.CreateSPKPage, name='create_spk'),

  path('pk/create/', pk_view.CreatePKPage, name='create_pk'),
  path('pk/get_pk_data/', pk_view.get_pk_data, name='get_pk_data'),
  path('pk/check_pk_in_spk/<uuid:spk_id>/', pk_view.check_pk_in_spk, name='check_pk_in_spk'),

  path('task/create/', task_view.CreateTaskPage, name='create_task'),
]
