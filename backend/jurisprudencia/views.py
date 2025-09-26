from datetime import datetime

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import (
    DjenSearchForm,
    TIPOS_DECISAO_PADRAO,
    TRIBUNAIS_PADRAO,
)
from .utils.djen_api import buscar_jurisprudencia_por_termo

ORIGEM_LABELS = {
    'cache': 'Cache 24h (Redis)',
    'djen': 'Consulta direta ao DJEN',
    'fallback': 'Fallback aplicado',
}


@require_http_methods(["GET", "POST"])
def djen_consulta_view(request):
    """Página Sprint 2 · T2/T8 para pesquisa de julgados via DJEN."""

    data = request.POST if request.method == 'POST' else request.GET

    resultado = None
    houve_busca = False
    origem_legenda = None

    form = DjenSearchForm(data or None)

    if data and any(value for key, value in data.items() if key != 'csrfmiddlewaretoken'):
        houve_busca = True

        if form.is_valid():
            # Busca real via DJEN por termo/filtros
            resultado = buscar_jurisprudencia_por_termo(form.cleaned_data)
            for item in resultado.get('julgados', []):
                data_iso = item.get('dataJulgamento')
                if data_iso:
                    try:
                        item['dataFormatada'] = datetime.fromisoformat(str(data_iso)).strftime('%d/%m/%Y')
                    except ValueError:
                        item['dataFormatada'] = data_iso
            origem_legenda = ORIGEM_LABELS.get(resultado.get('origem'), 'Consulta DJEN')
    
    form_data = form.cleaned_data if form.is_bound and form.is_valid() else {
        'termo': data.get('termo', '').strip() if data else '',
        'tribunais': data.getlist('tribunais') if hasattr(data, 'getlist') else [],
        'tipo_decisao': data.get('tipo_decisao', '') if data else '',
        'periodo_inicio': data.get('periodo_inicio', '') if data else '',
        'periodo_fim': data.get('periodo_fim', '') if data else '',
        'limite': data.get('limite', '25') if data else '25',
    }

    if isinstance(form_data.get('periodo_inicio'), datetime):
        form_data['periodo_inicio'] = form_data['periodo_inicio'].date().isoformat()
    elif hasattr(form_data.get('periodo_inicio'), 'isoformat'):
        form_data['periodo_inicio'] = form_data['periodo_inicio'].isoformat()

    if isinstance(form_data.get('periodo_fim'), datetime):
        form_data['periodo_fim'] = form_data['periodo_fim'].date().isoformat()
    elif hasattr(form_data.get('periodo_fim'), 'isoformat'):
        form_data['periodo_fim'] = form_data['periodo_fim'].isoformat()

    if isinstance(form_data.get('limite'), int):
        form_data['limite'] = str(form_data['limite'])

    contexto = {
        'form': form,
        'form_data': form_data,
        'resultado': resultado,
        'houve_busca': houve_busca,
        'tribunais_disponiveis': TRIBUNAIS_PADRAO,
        'tipos_decisao': TIPOS_DECISAO_PADRAO,
        'origem_labels': ORIGEM_LABELS,
        'origem_legenda': origem_legenda,
    }

    return render(request, 'jurisprudencia/djen_consulta.html', contexto)


@require_http_methods(["GET"])
def intimacoes_busca_view(request):
    # Rota descontinuada para Sprint 3; mantida para compatibilidade caso esteja linkada.
    return render(request, 'jurisprudencia/intimacoes_consulta.html', {
        'form': None,
        'itens': [],
        'houve_busca': False,
        'erro_msg': "Endpoint focado agora em /buscar/ (jurisprudência por termo via DJEN)",
    })
