from django.urls import path
from jardist.views import home_view, spk_view

urlpatterns = [
  path('', home_view.HomePage, name='home'),

  path('spk/create/', spk_view.CreateSPKPage, name='create_spk'),
]
