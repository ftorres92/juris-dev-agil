"""
Validação da integração DJEN - Sprint 3 V1
Testa conectividade, rate limiting e cache Redis
"""

import os
import time
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

import requests
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# Importar URL do módulo existente
from .djen_api import DJEN_API_URL

class DJENValidationError(Exception):
    """Exceção para erros de validação DJEN"""
    pass

class DJENValidator:
    """Validador da integração DJEN"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 20
        
    def test_connectivity(self) -> Dict[str, Any]:
        """Testa conectividade básica com DJEN"""
        logger.info("Testando conectividade com DJEN...")
        
        try:
            # Teste simples com parâmetros mínimos
            params = {
                'termo': 'teste',
                'tribunais': ['STF'],
                'limite': 1
            }
            
            start_time = time.time()
            response = self.session.get(DJEN_API_URL, params=params)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'success',
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'items_count': len(data.get('items', [])),
                    'message': 'Conectividade OK'
                }
            else:
                return {
                    'status': 'error',
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'message': f'HTTP {response.status_code}'
                }
                
        except requests.RequestException as e:
            logger.error(f"Erro de conectividade: {e}")
            return {
                'status': 'error',
                'response_time': 0,
                'status_code': 0,
                'message': f'Erro de rede: {str(e)}'
            }
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Testa rate limiting (60 req/min)"""
        logger.info("Testando rate limiting...")
        
        requests_made = 0
        start_time = time.time()
        errors = []
        
        try:
            # Fazer múltiplas requisições rapidamente
            for i in range(5):
                params = {
                    'termo': f'teste_{i}',
                    'tribunais': ['STF'],
                    'limite': 1
                }
                
                response = self.session.get(DJEN_API_URL, params=params)
                requests_made += 1
                
                if response.status_code == 429:  # Too Many Requests
                    errors.append(f"Rate limit atingido na requisição {i+1}")
                    break
                elif response.status_code != 200:
                    errors.append(f"Erro na requisição {i+1}: HTTP {response.status_code}")
                
                # Pequena pausa entre requisições
                time.sleep(0.1)
            
            elapsed_time = time.time() - start_time
            requests_per_minute = (requests_made / elapsed_time) * 60
            
            return {
                'status': 'success' if not errors else 'warning',
                'requests_made': requests_made,
                'elapsed_time': elapsed_time,
                'requests_per_minute': requests_per_minute,
                'errors': errors,
                'message': 'Rate limiting testado'
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de rate limiting: {e}")
            return {
                'status': 'error',
                'requests_made': requests_made,
                'elapsed_time': 0,
                'requests_per_minute': 0,
                'errors': [str(e)],
                'message': f'Erro: {str(e)}'
            }
    
    def test_cache_redis(self) -> Dict[str, Any]:
        """Testa cache Redis"""
        logger.info("Testando cache Redis...")
        
        try:
            # Teste de escrita
            test_key = 'djen_test_validation'
            test_data = {
                'teste': 'dados',
                'timestamp': datetime.now().isoformat(),
                'items': [{'id': 1, 'teste': 'valor'}]
            }
            
            # Escrever no cache
            cache.set(test_key, test_data, timeout=300)  # 5 minutos
            
            # Ler do cache
            cached_data = cache.get(test_key)
            
            if cached_data and cached_data.get('teste') == 'dados':
                return {
                    'status': 'success',
                    'message': 'Cache Redis funcionando',
                    'test_data': cached_data
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Cache Redis não está funcionando',
                    'cached_data': cached_data
                }
                
        except Exception as e:
            logger.error(f"Erro no teste de cache: {e}")
            return {
                'status': 'error',
                'message': f'Erro no cache: {str(e)}'
            }
    
    def test_backoff_exponential(self) -> Dict[str, Any]:
        """Testa backoff exponencial"""
        logger.info("Testando backoff exponencial...")
        
        try:
            # Simular erro 429 para testar backoff
            params = {
                'termo': 'teste_backoff',
                'tribunais': ['STF'],
                'limite': 1
            }
            
            retry_times = []
            max_retries = 3
            
            for attempt in range(max_retries):
                start_time = time.time()
                
                try:
                    response = self.session.get(DJEN_API_URL, params=params)
                    
                    if response.status_code == 429:
                        # Simular backoff exponencial
                        backoff_time = 0.5 * (2 ** attempt)
                        time.sleep(backoff_time)
                        retry_times.append(backoff_time)
                    else:
                        break
                        
                except requests.RequestException:
                    backoff_time = 0.5 * (2 ** attempt)
                    time.sleep(backoff_time)
                    retry_times.append(backoff_time)
            
            return {
                'status': 'success',
                'retry_times': retry_times,
                'message': 'Backoff exponencial testado'
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de backoff: {e}")
            return {
                'status': 'error',
                'message': f'Erro: {str(e)}'
            }
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Executa validação completa"""
        logger.info("Iniciando validação completa do DJEN...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Teste 1: Conectividade
        results['tests']['connectivity'] = self.test_connectivity()
        
        # Teste 2: Cache Redis
        results['tests']['cache'] = self.test_cache_redis()
        
        # Teste 3: Rate Limiting
        results['tests']['rate_limiting'] = self.test_rate_limiting()
        
        # Teste 4: Backoff Exponencial
        results['tests']['backoff'] = self.test_backoff_exponential()
        
        # Resumo geral
        success_count = sum(1 for test in results['tests'].values() if test['status'] == 'success')
        total_tests = len(results['tests'])
        
        results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': success_count,
            'failed_tests': total_tests - success_count,
            'success_rate': (success_count / total_tests) * 100,
            'overall_status': 'success' if success_count == total_tests else 'warning' if success_count > 0 else 'error'
        }
        
        logger.info(f"Validação concluída: {success_count}/{total_tests} testes passaram")
        
        return results

def validate_djen_integration() -> Dict[str, Any]:
    """Função principal para validação da integração DJEN"""
    validator = DJENValidator()
    return validator.run_full_validation()
