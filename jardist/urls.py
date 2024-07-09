from django.urls import path
from jardist.services import pk_service, task_service
from jardist.utils import download_all_documents
from jardist.views import spk_view, pk_view, task_view, auth_view

urlpatterns = [
  path('', pk_view.ListPKPage, name='list_pk'),
  path('login', auth_view.LoginPage, name='login'),
  path('logout', auth_view.Logout, name='logout'),

  path('spk/create', spk_view.CreateSPKPage, name='create_spk'),
  path('spk/edit/<uuid:spk_id>', spk_view.EditSPKPage, name='edit_spk'),

  path('pk/create', pk_view.CreatePKPage, name='create_pk'),
  path('pk/<uuid:pk_id>/view', pk_view.ViewPKPage, name='view_pk'),
  path('pk/<uuid:pk_id>/edit', pk_view.EditPKPage, name='edit_pk'),
  path('pk/<uuid:pk_id>/update-bast', pk_view.UpdateBASTPage, name='update_bast'),

  path('task/create', task_view.CreateTaskPage, name='create_task'),
  path('task/<uuid:task_id>/edit', task_view.EditTaskPage, name='edit_task'),
  path('task/<uuid:task_id>/edit-material', task_view.EditTaskMaterialPage, name='edit_task_material'),
  path('task/<uuid:task_id>/update-realization/material', task_view.UpdateRealizationTaskMaterialPage, name='update_realization_material'),
  path('task/<uuid:task_id>/add-material/rab', task_service.AddRABMaterial, name='add_rab_material'),
  path('task/<uuid:task_id>/add-material/realization', task_service.AddRealizationMaterial, name='add_realization_material'),
  path('task/documentation/create', task_view.CreateDocumentationPage, name='create_documentation'),
  path('task/documentation/view', task_view.ViewDocumentationPage, name='view_documentation'),

  path('archive/create', pk_view.CreateArchiveDocumentPage, name='create_archive_document'),
  path('archive/view', pk_view.ViewArchiveDocumentPage, name='view_archive_document'),

  path('api/get_pk_data', pk_service.get_pk_data, name='get_pk_data'),
  path('api/check_pk_in_spk/<uuid:spk_id>', pk_service.check_pk_in_spk, name='check_pk_in_spk'),
  path('api/get_task_data', task_service.get_task_data, name='get_task_data'),
  path('api/download-all-documents', download_all_documents, name='download_documents'),
]
