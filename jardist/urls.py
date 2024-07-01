from django.urls import path
from jardist.views import home_view, spk_view, pk_view, task_view
from jardist.services import pk_service, task_service

urlpatterns = [
  path('', home_view.HomePage, name='home'),

  path('spk/create', spk_view.CreateSPKPage, name='create_spk'),
  path('spk/edit/<uuid:spk_id>', spk_view.EditSPKPage, name='edit_spk'),

  path('pk/create', pk_view.CreatePKPage, name='create_pk'),
  path('pk/<uuid:pk_id>/view', pk_view.ViewPKPage, name='view_pk'),
  path('pk/<uuid:pk_id>/edit', pk_view.EditPKPage, name='edit_pk'),
  path('pk/<uuid:pk_id>/update-bast', pk_view.UpdateBASTPage, name='update_bast'),
  path('pk/get_pk_data', pk_service.get_pk_data, name='get_pk_data'),
  path('pk/check_pk_in_spk/<uuid:spk_id>', pk_service.check_pk_in_spk, name='check_pk_in_spk'),

  path('task/create', task_view.CreateTaskPage, name='create_task'),
  path('task/<uuid:task_id>/edit', task_view.EditTaskPage, name='edit_task'),
  path('task/<uuid:task_id>/edit-material', task_view.EditTaskMaterialPage, name='edit_task_material'),
  path('task/<uuid:task_id>/update-realization/task', task_view.UpdateRealizationTaskPage, name='update_realization_task'),
  path('task/<uuid:task_id>/update-realization/material', task_view.UpdateRealizationTaskMaterialPage, name='update_realization_material'),
  path('task/<uuid:task_id>/add-material/rab', task_service.AddRABMaterial, name='add_rab_material'),
  path('task/<uuid:task_id>/add-material/realization', task_service.AddRealizationMaterial, name='add_realization_material'),
]
