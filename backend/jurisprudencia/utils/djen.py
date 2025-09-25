from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from time import perf_counter
from typing import List

from django.db.models import Q, QuerySet

from ..models import Julgado


@dataclass(slots=True)
class DjenSearchParams:
    termo: str
    tribunais: List[str]
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
    tipo_decisao: str | None = None
    limite: int = 25


class DjenSearchResult(dict):
    """Estrutura simples para alinhar com o contrato esperado pelo frontend."""

    @property
    def julgados(self) -> List[dict]:  # type: ignore[override]
        return self['julgados']


class DJENCollector:
    """Coletor simplificado para consolidação Sprint 2 (T2/T8)."""

    def search(self, params: DjenSearchParams) -> DjenSearchResult:
        inicio = perf_counter()
        queryset = self._build_queryset(params)
        julgados = [self._serialize_julgado(julgado) for julgado in queryset[: params.limite]]
        execucao_ms = int((perf_counter() - inicio) * 1000)

        return DjenSearchResult(
            origem='cache' if julgados else 'djen',
            tempoExecucaoMs=execucao_ms,
            quantidade=len(julgados),
            julgados=julgados,
        )

    def _build_queryset(self, params: DjenSearchParams) -> QuerySet[Julgado]:
        queryset = Julgado.objects.all()

        if params.tribunais:
            queryset = queryset.filter(tribunal__in=params.tribunais)

        if params.periodo_inicio:
            queryset = queryset.filter(data_publicacao__gte=params.periodo_inicio)

        if params.periodo_fim:
            queryset = queryset.filter(data_publicacao__lte=params.periodo_fim)

        termo_normalizado = params.termo.strip()
        if termo_normalizado:
            queryset = queryset.filter(
                Q(titulo__icontains=termo_normalizado)
                | Q(conteudo__icontains=termo_normalizado)
                | Q(numero_processo__icontains=termo_normalizado)
            )

        return queryset.order_by('-data_publicacao')

    @staticmethod
    def _serialize_julgado(julgado: Julgado) -> dict:
        return {
            'id': str(julgado.id),
            'tribunal': julgado.tribunal,
            'vara': julgado.vara,
            'relator': julgado.relator,
            'dataJulgamento': julgado.data_publicacao.isoformat(),
            'tipoDecisao': None,
            'ementa': julgado.titulo,
            'decisao': julgado.conteudo,
            'url': julgado.url_original,
            'processo': julgado.numero_processo,
            'classe': None,
            'assunto': None,
            'scoreFavorabilidade': None,
        }


def build_search_params(payload: dict) -> DjenSearchParams:
    return DjenSearchParams(
        termo=payload['termo'],
        tribunais=payload['tribunais'],
        periodo_inicio=payload.get('periodo_inicio'),
        periodo_fim=payload.get('periodo_fim'),
        tipo_decisao=payload.get('tipo_decisao') or None,
        limite=payload.get('limite', 25),
    )
