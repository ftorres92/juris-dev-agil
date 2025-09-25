from datetime import datetime

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import (
    DjenSearchForm,
    TIPOS_DECISAO_PADRAO,
    TRIBUNAIS_PADRAO,
    IntimacoesBuscaForm,
)
from .utils.djen import DJENCollector, build_search_params
from .utils.intimacoes import (
    buscar_intimacoes,
    buscar_intimacoes_por_oab_string,
    buscar_intimacoes_por_nome,
)

ORIGEM_LABELS = {
    'cache': 'Cache 24h (Redis)',
    'djen': 'Consulta direta ao DJEN',
    'fallback': 'Fallback aplicado',
}


@require_http_methods(["GET", "POST"])
def djen_consulta_view(request):
    """Página Sprint 2 · T2/T8 para pesquisa de julgados via DJEN."""

    collector = DJENCollector()
    data = request.POST if request.method == 'POST' else request.GET

    resultado = None
    houve_busca = False
    origem_legenda = None

    form = DjenSearchForm(data or None)

    if data and any(value for key, value in data.items() if key != 'csrfmiddlewaretoken'):
        houve_busca = True

        if form.is_valid():
            params = build_search_params(form.cleaned_data)
            resultado = collector.search(params)
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
    """Busca e exibe intimações a partir do proxy DJEN externo.

    Suporta os três modos de consulta previstos no utilitário.
    """

    form = IntimacoesBuscaForm(request.GET or None)
    itens = []
    houve_busca = False
    erro_msg = None

    if request.GET and any(v for k, v in request.GET.items() if k != 'csrfmiddlewaretoken'):
        houve_busca = True
        if form.is_valid():
            data = form.cleaned_data
            try:
                if data["modo"] == "por_oab":
                    itens = buscar_intimacoes(
                        numero_oab=data["numero_oab"],
                        uf_oab=data["uf_oab"],
                        data_inicio=data.get("data_inicio").isoformat() if data.get("data_inicio") else None,
                        data_fim=data.get("data_fim").isoformat() if data.get("data_fim") else None,
                    )
                elif data["modo"] == "por_oab_string":
                    itens = buscar_intimacoes_por_oab_string(
                        oab_string=data["oab_string"],
                        data_inicio=data.get("data_inicio").isoformat() if data.get("data_inicio") else None,
                        data_fim=data.get("data_fim").isoformat() if data.get("data_fim") else None,
                    )
                else:
                    itens = buscar_intimacoes_por_nome(
                        nome_advogado=data.get("nome_advogado"),
                        nome_parte=data.get("nome_parte"),
                        data_inicio=data.get("data_inicio").isoformat() if data.get("data_inicio") else None,
                        data_fim=data.get("data_fim").isoformat() if data.get("data_fim") else None,
                        sigla_tribunal=data.get("sigla_tribunal"),
                        pagina=data.get("pagina"),
                        itens_por_pagina=data.get("itens_por_pagina"),
                    )
            except Exception as exc:  # pragma: no cover
                erro_msg = str(exc)

    contexto = {
        'form': form,
        'itens': itens,
        'houve_busca': houve_busca,
        'erro_msg': erro_msg,
    }
    return render(request, 'jurisprudencia/intimacoes_consulta.html', contexto)
