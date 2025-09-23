# DJEN Client - Sistema de Jurisprudência IA
# Baseado no modelo de microservico_api.py

import os
import requests
from requests.adapters import HTTPAdapter, Retry
from datetime import datetime
import time
import redis
import json
from typing import Dict, List, Optional, Any

class DJENClient:
    """
    Cliente para integração com DJEN (Diário da Justiça Eletrônico Nacional)
    
    Baseado no padrão do microservico_api.py com:
    - Rate limiting (60 req/min)
    - Cache Redis (24h)
    - Backoff exponencial
    - Retry automático
    """
    
    def __init__(self):
        # URL base do DJEN (baseada no modelo microservico_api.py)
        self.djen_url = os.getenv(
            "DJEN_API_URL",
            "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
        )
        
        # Configuração Redis para cache e rate limiting
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
        
        # Sessão HTTP com retry e backoff (igual ao modelo)
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Headers padrão
        self.headers = {
            "accept": "application/json",
            "accept-language": "pt-BR,pt;q=0.9",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
    
    def _check_rate_limit(self) -> bool:
        """
        Verifica e controla rate limiting (60 req/min)
        """
        current_minute = int(time.time() / 60)
        rate_key = f"djen_rate_limit:{current_minute}"
        
        # Incrementa contador
        current_requests = self.redis_client.incr(rate_key)
        self.redis_client.expire(rate_key, 60)  # Expira em 60 segundos
        
        if current_requests > 60:
            # Espera até o próximo minuto
            sleep_time = 60 - (time.time() % 60) + 1
            time.sleep(sleep_time)
            return False
        
        return True
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """
        Gera chave de cache baseada no endpoint e parâmetros
        """
        params_str = json.dumps(params, sort_keys=True)
        return f"djen_cache:{endpoint}:{hash(params_str)}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """
        Recupera dados do cache Redis
        """
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception:
            pass
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict, ttl: int = 86400):
        """
        Salva dados no cache Redis (24h por padrão)
        """
        try:
            self.redis_client.setex(cache_key, ttl, json.dumps(data))
        except Exception:
            pass
    
    def buscar_julgados(self, termo: str, **kwargs) -> Dict:
        """
        Busca julgados no DJEN (baseado no modelo microservico_api.py)
        
        Args:
            termo (str): Termo de busca
            **kwargs: Parâmetros adicionais (numeroOab, ufOab, dataInicio, etc.)
        
        Returns:
            Dict: Resposta da API com julgados encontrados
        """
        # Verificar rate limit
        self._check_rate_limit()
        
        # Montar parâmetros baseados no modelo
        params = {}
        
        # Parâmetros de OAB (como no modelo)
        if kwargs.get('numeroOab'):
            params['numeroOab'] = kwargs['numeroOab']
        if kwargs.get('ufOab'):
            params['ufOab'] = kwargs['ufOab']
        if kwargs.get('oabString'):
            params['numeroOab'] = kwargs['oabString']
        
        # Parâmetros de busca por nome/processo
        if kwargs.get('nomeAdvogado'):
            params['nomeAdvogado'] = kwargs['nomeAdvogado']
        if kwargs.get('nomeParte'):
            params['nomeParte'] = kwargs['nomeParte']
        if kwargs.get('numeroProcesso'):
            params['numeroProcesso'] = kwargs['numeroProcesso']
        
        # Parâmetros de data (como no modelo)
        if kwargs.get('dataInicio'):
            params['dataDisponibilizacaoInicio'] = kwargs['dataInicio']
        if kwargs.get('dataFim'):
            params['dataDisponibilizacaoFim'] = kwargs['dataFim']
        
        # Parâmetros adicionais
        if kwargs.get('siglaTribunal'):
            params['siglaTribunal'] = kwargs['siglaTribunal']
        if kwargs.get('numeroComunicacao'):
            params['numeroComunicacao'] = kwargs['numeroComunicacao']
        if kwargs.get('pagina'):
            params['pagina'] = kwargs['pagina']
        if kwargs.get('itensPorPagina'):
            params['itensPorPagina'] = kwargs['itensPorPagina']
        if kwargs.get('orgaoId'):
            params['orgaoId'] = kwargs['orgaoId']
        if kwargs.get('meio'):
            params['meio'] = kwargs['meio']
        
        # Verificar cache
        cache_key = self._get_cache_key('buscar_julgados', params)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Fazer requisição
            response = self.session.get(
                self.djen_url,
                params=params,
                headers=self.headers,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                # Salvar no cache
                self._save_to_cache(cache_key, data)
                return data
            else:
                return {
                    "status": "error",
                    "message": f"Erro na API DJEN: {response.status_code}",
                    "items": []
                }
                
        except requests.RequestException as e:
            return {
                "status": "error", 
                "message": f"Erro ao contatar DJEN: {str(e)}",
                "items": []
            }
    
    def health_check(self) -> Dict:
        """
        Verifica se a API DJEN está funcionando
        
        Returns:
            Dict: Status da API
        """
        try:
            response = self.session.get(
                self.djen_url,
                params={'pagina': 1, 'itensPorPagina': 1},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"status": "ok", "message": "API DJEN funcionando"}
            else:
                return {
                    "status": "error",
                    "message": f"API DJEN com problemas: {response.status_code}"
                }
                
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Erro ao verificar API DJEN: {str(e)}"
            }
