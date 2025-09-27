from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

from .djen_api import buscar_jurisprudencia_por_termo
from .search_query import (
    STOPWORDS_PT,
    compute_match_and_highlight,
    normalize_text,
    parse_query,
)


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value)
    return ''.join(ch for ch in normalized if not unicodedata.combining(ch))


def _unique(sequence: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in sequence:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


@dataclass(frozen=True)
class QueryVariation:
    termo: str
    motivo: str
    peso: float
    tipo: str


class NeutralSearchAgent:
    """Gera variações simples para ampliar a busca neutra de jurisprudência."""

    _SYMBOLS_TRANSLATIONS = str.maketrans({'"': '', "'": ''})

    _SYNONYM_MAP: Dict[str, Tuple[str, ...]] = {
        'responsabilidade': ('responsabilizacao', 'dever de indenizar'),
        'civil': ('civel',),
        'estado': ('ente publico', 'administracao publica'),
        'indenizacao': ('reparacao', 'ressarcimento'),
        'danos': ('prejuizos',),
        'tutela': ('liminar', 'provimento antecipado'),
        'urgencia': ('urgente', 'antecedente'),
        'contrato': ('contratual', 'acordo'),
        'contratos': ('contratual',),
        'trabalho': ('laboral', 'empregaticio'),
    }

    def __init__(self, max_variations: int = 5) -> None:
        self.max_variations = max(1, max_variations)

    def sugerir_variacoes(self, termo: str) -> List[QueryVariation]:
        base = ' '.join((termo or '').strip().split())
        if not base:
            return []

        variations: List[QueryVariation] = []
        append = variations.append

        append(QueryVariation(base, 'Termo informado pelo usuário', 1.0, 'original'))

        tokens = base.split()
        if len(tokens) > 1:
            quoted = f'"{base}"'
            append(QueryVariation(quoted, 'Prioriza a frase exata', 0.9, 'frase'))

            filtered_tokens = [tok for tok in tokens if normalize_text(tok) not in STOPWORDS_PT]
            sem_stop = ' '.join(filtered_tokens)
            if sem_stop and sem_stop.lower() != base.lower():
                append(QueryVariation(sem_stop, 'Foca em palavras-chave sem stopwords', 0.8, 'palavras-chave'))

        accentless = _strip_accents(base)
        if accentless and accentless.lower() != base.lower():
            append(QueryVariation(accentless, 'Ignora acentos para ampliar resultados', 0.7, 'acentos'))

        synonym_variation = self._synonym_variation(tokens)
        if synonym_variation:
            append(QueryVariation(synonym_variation, 'Inclui sinônimos jurídicos relevantes', 0.65, 'sinonimos'))

        unique_variations = _unique(qv.termo for qv in variations)[: self.max_variations]

        normalized_map = {qv.termo.lower(): qv for qv in variations}
        ordered: List[QueryVariation] = []
        for termo_variacao in unique_variations:
            key = termo_variacao.lower()
            ordered.append(normalized_map[key])
        return ordered

    def _synonym_variation(self, tokens: List[str]) -> str | None:
        if not tokens:
            return None

        replaced: List[str] = []
        used_synonym = False
        for token in tokens:
            normalized = normalize_text(token.translate(self._SYMBOLS_TRANSLATIONS))
            synonym_list = self._SYNONYM_MAP.get(normalized)
            if synonym_list and not used_synonym:
                replaced.append(synonym_list[0])
                used_synonym = True
            else:
                replaced.append(token)

        if not used_synonym:
            return None

        return ' '.join(replaced)


def executar_busca_neutra(cleaned_form: Dict[str, Any]) -> Dict[str, Any]:
    termo_base = (cleaned_form.get('termo') or '').strip()
    if not termo_base:
        return buscar_jurisprudencia_por_termo(cleaned_form)

    agente = NeutralSearchAgent()
    variacoes = agente.sugerir_variacoes(termo_base)
    if not variacoes:
        return buscar_jurisprudencia_por_termo(cleaned_form)

    base_query = parse_query(termo_base)
    limite = cleaned_form.get('limite') or 25
    try:
        limite = int(limite)
    except (TypeError, ValueError):
        limite = 25

    agregados: Dict[str, Dict[str, Any]] = {}
    relatorios_variacao: List[Dict[str, Any]] = []
    tempo_total_ms = 0

    for ordem, variacao in enumerate(variacoes):
        variacao_form = dict(cleaned_form)
        variacao_form['termo'] = variacao.termo
        resultado_variacao = buscar_jurisprudencia_por_termo(variacao_form)
        tempo_total_ms += resultado_variacao.get('tempoExecucaoMs', 0)

        relatorios_variacao.append(
            {
                'termo': variacao.termo,
                'motivo': variacao.motivo,
                'quantidade': resultado_variacao.get('quantidade', 0),
                'origem': resultado_variacao.get('origem', 'djen'),
                'peso': variacao.peso,
                'ordem': ordem,
            }
        )

        julgados = resultado_variacao.get('julgados') or []
        if not julgados:
            continue

        variacao_query = parse_query(variacao.termo)

        for julgado in julgados:
            unico = _definir_chave_unica(julgado)
            enriquecido = _enriquecer_julgado(
                julgado=julgado,
                base_query=base_query,
                variacao_query=variacao_query,
                variacao=variacao,
                ordem=ordem,
            )

            existente = agregados.get(unico)
            if existente is None or enriquecido['agenteScore'] > existente['agenteScore']:
                agregados[unico] = enriquecido

    lista_agregados = sorted(
        agregados.values(),
        key=lambda item: (
            item['agenteScore'],
            item.get('dataJulgamento') or item.get('dataFormatada') or '',
        ),
        reverse=True,
    )

    if limite > 0:
        lista_agregados = lista_agregados[:limite]

    return {
        'origem': 'agente_neutro',
        'tempoExecucaoMs': tempo_total_ms,
        'quantidade': len(lista_agregados),
        'julgados': lista_agregados,
        'variacoes': relatorios_variacao,
        'termoBase': termo_base,
    }


def _definir_chave_unica(julgado: Dict[str, Any]) -> str:
    for chave in ('id', 'processo', 'url', 'djen_id'):
        valor = julgado.get(chave)
        if valor:
            return str(valor)

    tribunal = julgado.get('tribunal') or 'desconhecido'
    data_referencia = julgado.get('dataJulgamento') or julgado.get('dataFormatada') or 's/d'
    ementa_raw = julgado.get('ementa_raw') or julgado.get('ementa') or ''
    base_resumo = normalize_text(ementa_raw)[:120]
    return f'{tribunal}|{data_referencia}|{base_resumo}'


def _enriquecer_julgado(
    *,
    julgado: Dict[str, Any],
    base_query,
    variacao_query,
    variacao: QueryVariation,
    ordem: int,
) -> Dict[str, Any]:
    texto_ementa = julgado.get('ementa_raw') or julgado.get('ementa') or ''
    texto_decisao = julgado.get('decisao') or ''

    combinado = f'{texto_ementa} {texto_decisao}'.strip()
    base_combinado_score, _ = compute_match_and_highlight(
        combinado,
        base_query,
        enforce_filters=False,
        highlight=False,
    )

    base_ementa_score, base_ementa_highlight = compute_match_and_highlight(
        texto_ementa,
        base_query,
        weight_multiplier=1.4,
        enforce_filters=False,
    )

    base_decisao_score, _ = compute_match_and_highlight(
        texto_decisao,
        base_query,
        enforce_filters=False,
        highlight=False,
    )

    score_base_total = max(base_combinado_score, base_ementa_score + base_decisao_score)

    # Aproveita score da variação quando base não retorna match
    score_variacao = julgado.get('matchScore') or 0
    if not score_variacao:
        score_variacao, _ = compute_match_and_highlight(
            texto_ementa,
            variacao_query,
            weight_multiplier=1.2,
            enforce_filters=False,
        )

    peso_variacao = variacao.peso or 0.5
    score_combinado = score_base_total if score_base_total > 0 else int(round(score_variacao * peso_variacao))
    minimo_variacao = 1 if score_variacao > 0 else 0
    score_final = max(score_base_total, score_combinado, minimo_variacao)

    ementa_destacada = base_ementa_highlight if score_base_total > 0 else julgado.get('ementa')

    enriquecido = dict(julgado)
    enriquecido['ementa'] = ementa_destacada or julgado.get('ementa')
    enriquecido['agenteInfo'] = {
        'variacaoTermo': variacao.termo,
        'motivo': variacao.motivo,
        'ordem': ordem,
        'peso': peso_variacao,
        'scoreBase': score_base_total,
        'scoreVariacao': score_variacao,
    }
    enriquecido['agenteScore'] = score_final
    return enriquecido
