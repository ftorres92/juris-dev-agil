import os
import logging
import requests
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

logger = logging.getLogger(__name__)


def buscar_intimacoes(
    numero_oab: str,
    uf_oab: str,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    raise_on_error: bool = False,
) -> List[Dict[str, Any]]:
    """Busca intimações no serviço proxy externo.

    Mantém a interface existente retornando uma lista (eventualmente vazia)
    e nunca lança exceção para o chamador quando raise_on_error=False.
    """

    url = os.getenv("INTIMACOES_API_URL", "http://localhost:5001/intimacoes")
    params: Dict[str, Any] = {
        "numeroOab": numero_oab,
        "ufOab": uf_oab,
    }
    if data_inicio:
        params["dataInicio"] = data_inicio
    if data_fim:
        params["dataFim"] = data_fim

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as exc:
        logger.error("Erro de rede ao buscar intimações: %s", str(exc))
        if raise_on_error:
            raise
        return []

    if response.status_code == 200:
        try:
            dados = response.json()
        except ValueError:
            logger.error("Resposta 200 não é JSON válido: %s", response.text[:500])
            if raise_on_error:
                raise ValueError("Resposta 200 não é JSON válido")
            return []
        return dados.get("items", []) if isinstance(dados, dict) else []

    logger.warning(
        "Erro ao buscar intimações: %s %s",
        response.status_code,
        response.text[:500] if response.text else "<sem corpo>",
    )
    if raise_on_error:
        raise RuntimeError(f"HTTP {response.status_code} ao buscar intimações")
    return []


def buscar_intimacoes_por_oab_string(
    oab_string: str,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    raise_on_error: bool = False,
) -> List[Dict[str, Any]]:
    """Busca intimações usando numeroOab como string (ex.: 'SP07749'), sem UF separada.

    Mantém contrato de retornar lista e não lançar exceção quando raise_on_error=False.
    """

    if not oab_string:
        return []

    url = os.getenv("INTIMACOES_API_URL", "http://localhost:5001/intimacoes")
    params: Dict[str, Any] = {
        "numeroOab": oab_string,
    }
    if data_inicio:
        params["dataInicio"] = data_inicio
    if data_fim:
        params["dataFim"] = data_fim

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as exc:
        logger.error("Erro de rede ao buscar intimações por oab-string: %s", str(exc))
        if raise_on_error:
            raise
        return []

    if response.status_code == 200:
        try:
            dados = response.json()
        except ValueError:
            logger.error("Resposta 200 não é JSON válido (por oab-string): %s", response.text[:500])
            if raise_on_error:
                raise ValueError("Resposta 200 não é JSON válido")
            return []
        return dados.get("items", []) if isinstance(dados, dict) else []

    logger.warning(
        "Erro ao buscar intimações por oab-string: %s %s",
        response.status_code,
        response.text[:500] if response.text else "<sem corpo>",
    )
    if raise_on_error:
        raise RuntimeError(f"HTTP {response.status_code} ao buscar intimações por oab-string")
    return []


def buscar_intimacoes_por_nome(
    nome_advogado: Optional[str] = None,
    nome_parte: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    sigla_tribunal: Optional[str] = None,
    pagina: Optional[int] = None,
    itens_por_pagina: Optional[int] = None,
    raise_on_error: bool = False,
) -> List[Dict[str, Any]]:
    """Busca intimações por nome (advogado e/ou parte) no serviço proxy externo.

    Parâmetros conforme Swagger:
      - nomeAdvogado, nomeParte
      - dataDisponibilizacaoInicio, dataDisponibilizacaoFim (yyyy-mm-dd)
      - siglaTribunal
      - pagina, itensPorPagina (5 ou 100)

    Retorna lista com as intimações (ou lista vazia em caso de erro quando
    raise_on_error=False).
    """

    if not nome_advogado and not nome_parte:
        return []

    url = os.getenv("INTIMACOES_API_URL", "http://localhost:5001/intimacoes")

    params: Dict[str, Any] = {}
    if nome_advogado:
        params["nomeAdvogado"] = nome_advogado
    if nome_parte:
        params["nomeParte"] = nome_parte
    if data_inicio:
        params["dataDisponibilizacaoInicio"] = data_inicio
    if data_fim:
        params["dataDisponibilizacaoFim"] = data_fim
    if sigla_tribunal:
        params["siglaTribunal"] = sigla_tribunal
    if pagina is not None:
        params["pagina"] = pagina
    if itens_por_pagina is not None:
        params["itensPorPagina"] = itens_por_pagina

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as exc:
        logger.error("Erro de rede ao buscar intimações por nome: %s", str(exc))
        if raise_on_error:
            raise
        return []

    if response.status_code == 200:
        try:
            dados = response.json()
        except ValueError:
            logger.error("Resposta 200 não é JSON válido (por nome): %s", response.text[:500])
            if raise_on_error:
                raise ValueError("Resposta 200 não é JSON válido")
            return []
        return dados.get("items", []) if isinstance(dados, dict) else []

    logger.warning(
        "Erro ao buscar intimações por nome: %s %s",
        response.status_code,
        response.text[:500] if response.text else "<sem corpo>",
    )
    if raise_on_error:
        raise RuntimeError(f"HTTP {response.status_code} ao buscar intimações por nome")
    return []


