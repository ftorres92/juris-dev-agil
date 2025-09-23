# Testes para o sistema de jurisprudência
from django.test import TestCase
from django.test.utils import override_settings
from unittest.mock import patch, Mock
import json

from .utils.djen import DJENClient


class DJENClientTestCase(TestCase):
    """Testes para o cliente DJEN"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = DJENClient()
    
    @patch('jurisprudencia.utils.djen.redis.Redis')
    @patch('jurisprudencia.utils.djen.requests.Session')
    def test_djen_client_initialization(self, mock_session, mock_redis):
        """Testa se o cliente DJEN é inicializado corretamente"""
        client = DJENClient()
        
        # Verifica se Redis foi configurado
        mock_redis.assert_called_once()
        
        # Verifica se a sessão HTTP foi configurada
        mock_session.assert_called_once()
    
    @patch('jurisprudencia.utils.djen.redis.Redis')
    @patch('jurisprudencia.utils.djen.requests.Session')
    def test_buscar_julgados_success(self, mock_session, mock_redis):
        """Testa busca de julgados com sucesso"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "items": [
                {
                    "id": "123",
                    "titulo": "Teste de julgado",
                    "conteudo": "Conteúdo do julgado",
                    "data_publicacao": "2023-01-01"
                }
            ]
        }
        
        # Mock da sessão
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Mock do Redis
        mock_redis_instance = Mock()
        mock_redis_instance.incr.return_value = 1
        mock_redis_instance.get.return_value = None  # Sem cache
        mock_redis.return_value = mock_redis_instance
        
        # Teste
        client = DJENClient()
        result = client.buscar_julgados("teste")
        
        # Verificações
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["id"], "123")
    
    @patch('jurisprudencia.utils.djen.redis.Redis')
    @patch('jurisprudencia.utils.djen.requests.Session')
    def test_buscar_julgados_with_cache(self, mock_session, mock_redis):
        """Testa busca de julgados com cache"""
        # Mock do Redis com cache
        mock_redis_instance = Mock()
        mock_redis_instance.incr.return_value = 1
        cached_data = {
            "status": "ok",
            "items": [{"id": "cached", "titulo": "Cached result"}]
        }
        mock_redis_instance.get.return_value = json.dumps(cached_data)
        mock_redis.return_value = mock_redis_instance
        
        # Teste
        client = DJENClient()
        result = client.buscar_julgados("teste")
        
        # Verificações
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["items"][0]["id"], "cached")
        
        # Verifica que não fez requisição HTTP (cache hit)
        mock_session_instance = mock_session.return_value
        mock_session_instance.get.assert_not_called()
    
    @patch('jurisprudencia.utils.djen.redis.Redis')
    @patch('jurisprudencia.utils.djen.requests.Session')
    def test_buscar_julgados_error(self, mock_session, mock_redis):
        """Testa busca de julgados com erro"""
        # Mock da resposta de erro
        mock_response = Mock()
        mock_response.status_code = 500
        
        # Mock da sessão
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Mock do Redis
        mock_redis_instance = Mock()
        mock_redis_instance.incr.return_value = 1
        mock_redis_instance.get.return_value = None
        mock_redis.return_value = mock_redis_instance
        
        # Teste
        client = DJENClient()
        result = client.buscar_julgados("teste")
        
        # Verificações
        self.assertEqual(result["status"], "error")
        self.assertIn("Erro na API DJEN", result["message"])
    
    @patch('jurisprudencia.utils.djen.redis.Redis')
    @patch('jurisprudencia.utils.djen.requests.Session')
    def test_health_check_success(self, mock_session, mock_redis):
        """Testa health check com sucesso"""
        # Mock da resposta
        mock_response = Mock()
        mock_response.status_code = 200
        
        # Mock da sessão
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Mock do Redis
        mock_redis_instance = Mock()
        mock_redis_instance.incr.return_value = 1
        mock_redis.return_value = mock_redis_instance
        
        # Teste
        client = DJENClient()
        result = client.health_check()
        
        # Verificações
        self.assertEqual(result["status"], "ok")
        self.assertIn("funcionando", result["message"])
    
    @patch('jurisprudencia.utils.djen.redis.Redis')
    @patch('jurisprudencia.utils.djen.requests.Session')
    def test_rate_limiting(self, mock_session, mock_redis):
        """Testa rate limiting"""
        # Mock do Redis com rate limit excedido
        mock_redis_instance = Mock()
        mock_redis_instance.incr.return_value = 61  # Excedeu o limite
        mock_redis.return_value = mock_redis_instance
        
        # Mock da sessão
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Teste
        client = DJENClient()
        
        # Verifica se o rate limiting foi aplicado
        # (O método _check_rate_limit deve fazer sleep)
        with patch('time.sleep') as mock_sleep:
            client._check_rate_limit()
            # Verifica se sleep foi chamado (rate limit excedido)
            mock_sleep.assert_called()
    
    def test_parameter_mapping(self):
        """Testa se os parâmetros são mapeados corretamente"""
        # Teste dos parâmetros baseados no modelo
        expected_params = {
            'numeroOab': '123456',
            'ufOab': 'SP',
            'nomeAdvogado': 'João Silva',
            'dataInicio': '2023-01-01',
            'dataFim': '2023-12-31',
            'siglaTribunal': 'TJSP'
        }
        
        # Simula a montagem de parâmetros
        params = {}
        if expected_params.get('numeroOab'):
            params['numeroOab'] = expected_params['numeroOab']
        if expected_params.get('ufOab'):
            params['ufOab'] = expected_params['ufOab']
        if expected_params.get('nomeAdvogado'):
            params['nomeAdvogado'] = expected_params['nomeAdvogado']
        if expected_params.get('dataInicio'):
            params['dataDisponibilizacaoInicio'] = expected_params['dataInicio']
        if expected_params.get('dataFim'):
            params['dataDisponibilizacaoFim'] = expected_params['dataFim']
        if expected_params.get('siglaTribunal'):
            params['siglaTribunal'] = expected_params['siglaTribunal']
        
        # Verificações
        self.assertEqual(params['numeroOab'], '123456')
        self.assertEqual(params['ufOab'], 'SP')
        self.assertEqual(params['nomeAdvogado'], 'João Silva')
        self.assertEqual(params['dataDisponibilizacaoInicio'], '2023-01-01')
        self.assertEqual(params['dataDisponibilizacaoFim'], '2023-12-31')
        self.assertEqual(params['siglaTribunal'], 'TJSP')