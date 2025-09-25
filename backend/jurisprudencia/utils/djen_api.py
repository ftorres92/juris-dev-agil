from __future__ import annotations

import os
import logging
from datetime import datetime
from time import perf_counter
from typing import Any, Dict, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .html_sanitizer import sanitize_fragment

logger = logging.getLogger(__name__)


# Sessão HTTP resiliente
_session = requests.Session()
_retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
_adapter = HTTPAdapter(max_retries=_retries)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)


DJEN_API_URL = os.getenv(
    "DJEN_API_URL",
    # Por padrão, aponta para comunica API (conforme exemplo do usuário)
    "https://comunicaapi.pje.jus.br/api/v1/comunicacao",
)


def _iso_date(value: Any) -> str | None:
    if not value:
        return None
    try:
        # aceita "YYYY-MM-DD" e retorna string
        if isinstance(value, str) and len(value) == 10:
            datetime.strptime(value, "%Y-%m-%d")
            return value
    except Exception:
        return None
    return str(value)


def build_params_from_busca_form(cleaned: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia campos do formulário para a API do DJEN (comunicacao)."""
    params: Dict[str, Any] = {}

    termo = (cleaned.get("termo") or "").strip()
    if termo:
        # A API de comunicação aceita busca textual em "texto". Alguns proxies aceitam "termo".
        # Enviaremos ambos para compatibilidade.
        params["texto"] = termo
        params["termo"] = termo

    # Campo no formulário é 'tribunais' (lista). Se houver apenas um selecionado, mapeia para siglaTribunal
    tribunais = cleaned.get("tribunais") or []
    if isinstance(tribunais, (list, tuple)) and len(tribunais) == 1:
        params["siglaTribunal"] = tribunais[0]
    elif isinstance(tribunais, (list, tuple)) and len(tribunais) > 1:
        # Alguns gateways aceitam parâmetro repetido. O requests expande listas em múltiplos params.
        params["siglaTribunal"] = tribunais

    if cleaned.get("data_inicio"):
        params["dataDisponibilizacaoInicio"] = _iso_date(cleaned["data_inicio"]) or cleaned["data_inicio"]
    if cleaned.get("data_fim"):
        params["dataDisponibilizacaoFim"] = _iso_date(cleaned["data_fim"]) or cleaned["data_fim"]

    if cleaned.get("numero_processo"):
        params["numeroProcesso"] = cleaned["numero_processo"]

    # paginação básica
    limite = cleaned.get("limite") or 25
    params["itensPorPagina"] = int(limite)
    params["pagina"] = 1

    return params


def _chamar_djen(params: Dict[str, Any]) -> Dict[str, Any]:
    inicio = perf_counter()
    try:
        resp = _session.get(DJEN_API_URL, params=params, timeout=20)
        tempo_ms = int((perf_counter() - inicio) * 1000)
    except requests.RequestException as exc:
        logger.error("Erro ao consultar DJEN: %s", str(exc))
        return {"origem": "djen", "tempoExecucaoMs": 0, "items": []}

    if resp.status_code != 200:
        logger.warning("DJEN HTTP %s: %s", resp.status_code, resp.text[:500])
        return {"origem": "djen", "tempoExecucaoMs": tempo_ms, "items": []}

    try:
        data = resp.json()
    except ValueError:
        logger.error("Resposta DJEN não é JSON: %s", resp.text[:500])
        return {"origem": "djen", "tempoExecucaoMs": tempo_ms, "items": []}

    data["tempoExecucaoMs"] = tempo_ms
    data.setdefault("origem", "djen")
    return data


def _mapear_para_julgados(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    julgados: List[Dict[str, Any]] = []
    for it in items:
        data_pub = it.get("data_disponibilizacao") or it.get("datadisponibilizacao")
        ementa = it.get("texto")
        ementa = sanitize_fragment(ementa) if isinstance(ementa, str) else ementa
        julgados.append(
            {
                "id": it.get("id"),
                "tribunal": it.get("siglaTribunal"),
                "vara": it.get("nomeOrgao"),
                "relator": None,
                "dataJulgamento": data_pub,
                "ementa": ementa,
                "decisao": ementa,
                "url": it.get("link"),
                "processo": it.get("numero_processo") or it.get("numeroprocessocommascara"),
                "classe": it.get("nomeClasse"),
                "assunto": None,
                "scoreFavorabilidade": None,
            }
        )
    return julgados


def buscar_jurisprudencia_por_termo(cleaned_form: Dict[str, Any]) -> Dict[str, Any]:
    """Realiza busca de 'jurisprudência' via DJEN por termo e filtros.

    Retorna estrutura compatível com o template `djen_consulta.html`:
      { origem, tempoExecucaoMs, quantidade, julgados }
    """
    params = build_params_from_busca_form(cleaned_form)
    data = _chamar_djen(params)
    items = data.get("items") or []
    julgados = _mapear_para_julgados(items)
    return {
        "origem": data.get("origem", "djen"),
        "tempoExecucaoMs": data.get("tempoExecucaoMs", 0),
        "quantidade": len(julgados),
        "julgados": julgados,
    }


