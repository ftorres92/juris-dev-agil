"""
Verificação de integridade dos dados DJEN - Sprint 3 V2
Valida estrutura de resposta, campos obrigatórios e consistência
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DataIntegrityError(Exception):
    """Exceção para erros de integridade de dados"""
    pass

class DJENDataValidator:
    """Validador de integridade dos dados DJEN"""
    
    def __init__(self):
        self.required_fields = [
            'tribunal', 'dataJulgamento', 'ementa'  # Removido 'id' que não existe no código atual
        ]
        
        self.optional_fields = [
            'decisao', 'relator', 'vara', 'comarca', 'url', 'metadados'
        ]
        
        self.expected_tribunals = [
            'STF', 'STJ', 'TST', 'TSE', 'STM',
            'TRF-1', 'TRF-2', 'TRF-3', 'TRF-4', 'TRF-5',
            'TRT-1', 'TRT-2', 'TRT-3', 'TRT-4', 'TRT-5',
            'TRE-AC', 'TRE-AL', 'TRE-AP', 'TRE-AM', 'TRE-BA',
            'TJ-AC', 'TJ-AL', 'TJ-AP', 'TJ-AM', 'TJ-BA'
        ]
    
    def validate_response_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida estrutura básica da resposta"""
        logger.info("Validando estrutura da resposta...")
        
        issues = []
        
        # Verificar campos obrigatórios no nível raiz
        root_required = ['origem', 'tempoExecucaoMs']
        for field in root_required:
            if field not in data:
                issues.append(f"Campo obrigatório '{field}' ausente na resposta")
        
        # Verificar se 'julgados' existe e é lista (estrutura do código existente)
        if 'julgados' not in data:
            issues.append("Campo 'julgados' ausente na resposta")
        elif not isinstance(data['julgados'], list):
            issues.append("Campo 'julgados' deve ser uma lista")
        else:
            # Validar cada item
            for i, item in enumerate(data['julgados']):
                item_issues = self.validate_item_structure(item, i)
                issues.extend(item_issues)
        
        return {
            'status': 'success' if not issues else 'error',
            'issues': issues,
            'items_count': len(data.get('julgados', [])),
            'message': 'Estrutura validada' if not issues else f'{len(issues)} problemas encontrados'
        }
    
    def validate_item_structure(self, item: Dict[str, Any], index: int) -> List[str]:
        """Valida estrutura de um item individual"""
        issues = []
        
        # Verificar campos obrigatórios
        for field in self.required_fields:
            if field not in item:
                issues.append(f"Item {index}: campo obrigatório '{field}' ausente")
            elif not item[field]:
                issues.append(f"Item {index}: campo '{field}' vazio")
        
        # Validar tipos de dados
        if 'dataJulgamento' in item:
            if not self.validate_date_format(item['dataJulgamento']):
                issues.append(f"Item {index}: formato de data inválido")
        
        if 'tribunal' in item:
            if not self.validate_tribunal(item['tribunal']):
                issues.append(f"Item {index}: tribunal '{item['tribunal']}' não reconhecido")
        
        # Validar encoding de caracteres especiais
        if 'ementa' in item:
            if not self.validate_encoding(item['ementa']):
                issues.append(f"Item {index}: problemas de encoding na ementa")
        
        return issues
    
    def validate_date_format(self, date_str: str) -> bool:
        """Valida formato de data"""
        try:
            if isinstance(date_str, str):
                # Aceitar formatos: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS
                if len(date_str) >= 10:
                    datetime.fromisoformat(date_str[:10])
                    return True
            return False
        except ValueError:
            return False
    
    def validate_tribunal(self, tribunal: str) -> bool:
        """Valida se tribunal é reconhecido"""
        return tribunal in self.expected_tribunals
    
    def validate_encoding(self, text: str) -> bool:
        """Valida encoding de texto"""
        try:
            # Tentar decodificar como UTF-8
            text.encode('utf-8').decode('utf-8')
            return True
        except UnicodeError:
            return False
    
    def validate_data_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida consistência dos dados"""
        logger.info("Validando consistência dos dados...")
        
        issues = []
        items = data.get('julgados', [])
        
        if not items:
            return {
                'status': 'warning',
                'issues': ['Nenhum item retornado'],
                'message': 'Dados vazios'
            }
        
        # Verificar duplicatas por tribunal + data (já que não temos ID único)
        tribunal_data = [(item.get('tribunal'), item.get('dataJulgamento')) for item in items if item.get('tribunal') and item.get('dataJulgamento')]
        if len(tribunal_data) != len(set(tribunal_data)):
            issues.append("Combinações tribunal+data duplicadas encontradas")
        
        # Verificar consistência de tribunais
        tribunals = [item.get('tribunal') for item in items if item.get('tribunal')]
        unique_tribunals = set(tribunals)
        if len(unique_tribunals) > 1:
            issues.append(f"Múltiplos tribunais em uma consulta: {unique_tribunals}")
        
        # Verificar datas
        dates = [item.get('dataJulgamento') for item in items if item.get('dataJulgamento')]
        if dates:
            try:
                parsed_dates = [datetime.fromisoformat(d[:10]) for d in dates if d]
                if parsed_dates:
                    min_date = min(parsed_dates)
                    max_date = max(parsed_dates)
                    if (max_date - min_date).days > 365:
                        issues.append("Período de datas muito amplo (> 1 ano)")
            except ValueError:
                issues.append("Datas em formato inválido")
        
        return {
            'status': 'success' if not issues else 'warning',
            'issues': issues,
            'items_count': len(items),
            'unique_tribunals': len(unique_tribunals),
            'message': 'Consistência validada' if not issues else f'{len(issues)} problemas de consistência'
        }
    
    def validate_performance_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida métricas de performance"""
        logger.info("Validando métricas de performance...")
        
        issues = []
        
        # Verificar tempo de execução
        tempo_execucao = data.get('tempoExecucaoMs', 0)
        if tempo_execucao > 10000:  # 10 segundos
            issues.append(f"Tempo de execução muito alto: {tempo_execucao}ms")
        
        # Verificar quantidade de itens
        items_count = len(data.get('julgados', []))
        if items_count > 100:
            issues.append(f"Quantidade de itens muito alta: {items_count}")
        
        # Verificar tamanho da resposta
        import sys
        response_size = sys.getsizeof(data)
        if response_size > 1024 * 1024:  # 1MB
            issues.append(f"Resposta muito grande: {response_size} bytes")
        
        return {
            'status': 'success' if not issues else 'warning',
            'issues': issues,
            'tempo_execucao_ms': tempo_execucao,
            'items_count': items_count,
            'response_size_bytes': response_size,
            'message': 'Métricas validadas' if not issues else f'{len(issues)} problemas de performance'
        }
    
    def run_full_integrity_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa verificação completa de integridade"""
        logger.info("Iniciando verificação completa de integridade...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Verificação 1: Estrutura
        results['checks']['structure'] = self.validate_response_structure(data)
        
        # Verificação 2: Consistência
        results['checks']['consistency'] = self.validate_data_consistency(data)
        
        # Verificação 3: Performance
        results['checks']['performance'] = self.validate_performance_metrics(data)
        
        # Resumo geral
        total_issues = sum(
            len(check.get('issues', [])) 
            for check in results['checks'].values()
        )
        
        results['summary'] = {
            'total_issues': total_issues,
            'structure_issues': len(results['checks']['structure'].get('issues', [])),
            'consistency_issues': len(results['checks']['consistency'].get('issues', [])),
            'performance_issues': len(results['checks']['performance'].get('issues', [])),
            'overall_status': 'success' if total_issues == 0 else 'warning' if total_issues < 5 else 'error'
        }
        
        logger.info(f"Verificação de integridade concluída: {total_issues} problemas encontrados")
        
        return results

def validate_djen_data_integrity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Função principal para validação de integridade dos dados"""
    validator = DJENDataValidator()
    return validator.run_full_integrity_check(data)
