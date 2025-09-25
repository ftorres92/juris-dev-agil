from django.urls import path

from .views import djen_consulta_view, intimacoes_busca_view

app_name = 'jurisprudencia'

urlpatterns = [
    path('djen/consulta/', djen_consulta_view, name='djen-consulta'),
    path('buscar/', intimacoes_busca_view, name='buscar_jurisprudencia'),
    path('intimacoes/buscar/', intimacoes_busca_view, name='intimacoes-buscar'),
]
