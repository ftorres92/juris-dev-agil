from django.urls import path

from .views import djen_consulta_view

app_name = 'jurisprudencia'

urlpatterns = [
    path('djen/consulta/', djen_consulta_view, name='djen-consulta'),
]
