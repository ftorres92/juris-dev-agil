"""
Integração dos arquivos de validação com o código existente
Sprint 3 - Conecta djen_validation.py e data_integrity.py com djen_api.py
"""

import logging
from typing import Dict, Any

from .djen_api import buscar_jurisprudencia_por_termo
from .djen_validation import validate_djen_integration
from .data_integrity import validate_djen_data_integrity

logger = logging.getLogger(__name__)

def validate_and_search_jurisprudencia(cleaned_form: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função integrada que valida a integração DJEN e depois faz a busca
    Conecta os arquivos de validação com o código existente
    """
    logger.info("Iniciando validação integrada da busca DJEN...")
    
    # Passo 1: Validar integração DJEN (V1)
    logger.info("Executando V1 - Validação DJENCollector...")
    validation_results = validate_djen_integration()
    
    if validation_results['summary']['overall_status'] != 'success':
        logger.warning("Validação DJEN falhou, mas continuando com busca...")
        # Continuar mesmo com falhas de validação para não quebrar o fluxo
    
    # Passo 2: Fazer busca usando código existente
    logger.info("Executando busca via djen_api.py...")
    try:
        search_results = buscar_jurisprudencia_por_termo(cleaned_form)
        
        # Passo 3: Validar integridade dos dados (V2)
        logger.info("Executando V2 - Verificação integridade dos dados...")
        integrity_results = validate_djen_data_integrity(search_results)
        
        # Adicionar resultados de validação ao resultado da busca
        search_results['validation'] = {
            'djen_integration': validation_results,
            'data_integrity': integrity_results,
            'overall_status': 'success' if (
                validation_results['summary']['overall_status'] == 'success' and
                integrity_results['summary']['overall_status'] in ['success', 'warning']
            ) else 'warning'
        }
        
        logger.info("Validação integrada concluída com sucesso")
        return search_results
        
    except Exception as e:
        logger.error(f"Erro durante busca integrada: {e}")
        return {
            'origem': 'error',
            'tempoExecucaoMs': 0,
            'julgados': [],
            'validation': {
                'djen_integration': validation_results,
                'data_integrity': {'summary': {'overall_status': 'error'}},
                'overall_status': 'error',
                'error': str(e)
            }
        }

def run_health_check() -> Dict[str, Any]:
    """
    Executa health check completo do sistema DJEN
    Útil para monitoramento e diagnóstico
    """
    logger.info("Executando health check completo...")
    
    # Teste de conectividade básica
    test_form = {
        'termo': 'teste',
        'tribunais': ['STF'],
        'limite': 1
    }
    
    try:
        results = validate_and_search_jurisprudencia(test_form)
        
        return {
            'status': 'healthy' if results['validation']['overall_status'] == 'success' else 'degraded',
            'timestamp': results.get('validation', {}).get('djen_integration', {}).get('timestamp'),
            'djen_connectivity': results['validation']['djen_integration']['summary']['overall_status'],
            'data_integrity': results['validation']['data_integrity']['summary']['overall_status'],
            'julgados_count': len(results.get('julgados', [])),
            'response_time_ms': results.get('tempoExecucaoMs', 0)
        }
        
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': None
        }

def get_validation_summary() -> Dict[str, Any]:
    """
    Retorna resumo das validações para dashboard/monitoramento
    """
    try:
        # Validação DJEN
        djen_validation = validate_djen_integration()
        
        # Teste de integridade com dados de exemplo
        test_data = {
            'origem': 'test',
            'tempoExecucaoMs': 1000,
            'julgados': [
                {
                    'tribunal': 'STF',
                    'dataJulgamento': '2024-01-01',
                    'ementa': 'Teste de ementa'
                }
            ]
        }
        integrity_validation = validate_djen_data_integrity(test_data)
        
        return {
            'djen_integration': {
                'status': djen_validation['summary']['overall_status'],
                'success_rate': djen_validation['summary']['success_rate'],
                'tests_passed': djen_validation['summary']['successful_tests'],
                'total_tests': djen_validation['summary']['total_tests']
            },
            'data_integrity': {
                'status': integrity_validation['summary']['overall_status'],
                'total_issues': integrity_validation['summary']['total_issues'],
                'structure_issues': integrity_validation['summary']['structure_issues'],
                'consistency_issues': integrity_validation['summary']['consistency_issues'],
                'performance_issues': integrity_validation['summary']['performance_issues']
            },
            'overall_health': 'healthy' if (
                djen_validation['summary']['overall_status'] == 'success' and
                integrity_validation['summary']['overall_status'] in ['success', 'warning']
            ) else 'degraded'
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter resumo de validação: {e}")
        return {
            'djen_integration': {'status': 'error', 'error': str(e)},
            'data_integrity': {'status': 'error', 'error': str(e)},
            'overall_health': 'unhealthy'
        }
