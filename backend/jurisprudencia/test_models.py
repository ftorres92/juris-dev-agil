# Testes para os modelos Django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from decimal import Decimal
import json

from .models import (
    Julgado, AnaliseJurisprudenciaTese, JulgadoFavoravel,
    AnaliseJurisprudenciaNeutra, PadroesVaraTribunal, EstrategiaAntecipatoria
)

User = get_user_model()


class JulgadoModelTestCase(TestCase):
    """Testes para o modelo Julgado"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_julgado(self):
        """Testa criação de julgado"""
        julgado = Julgado.objects.create(
            numero_processo="1234567-12.2023.8.26.0001",
            titulo="RESPONSABILIDADE CIVIL. DANO MORAL.",
            conteudo="Conteúdo completo do julgado...",
            data_publicacao=date.today(),
            tribunal="TJSP",
            vara="1ª Vara Cível",
            comarca="São Paulo",
            relator="Des. João Silva",
            djen_id="TJSP123456",
            hash_conteudo="abc123def456",
            criado_por=self.user
        )
        
        self.assertEqual(julgado.numero_processo, "1234567-12.2023.8.26.0001")
        self.assertEqual(julgado.tribunal, "TJSP")
        self.assertFalse(julgado.processado)
        self.assertEqual(str(julgado), "1234567-12.2023.8.26.0001 - TJSP")
    
    def test_unique_djen_id(self):
        """Testa que djen_id deve ser único"""
        Julgado.objects.create(
            numero_processo="1234567-12.2023.8.26.0001",
            titulo="Teste 1",
            conteudo="Conteúdo 1",
            data_publicacao=date.today(),
            tribunal="TJSP",
            djen_id="UNIQUE_ID_123",
            hash_conteudo="hash1",
            criado_por=self.user
        )
        
        with self.assertRaises(IntegrityError):
            Julgado.objects.create(
                numero_processo="7654321-12.2023.8.26.0002",
                titulo="Teste 2",
                conteudo="Conteúdo 2",
                data_publicacao=date.today(),
                tribunal="TJRJ",
                djen_id="UNIQUE_ID_123",  # ID duplicado
                hash_conteudo="hash2",
                criado_por=self.user
            )


class AnaliseJurisprudenciaTeseTestCase(TestCase):
    """Testes para o modelo AnaliseJurisprudenciaTese"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.julgado = Julgado.objects.create(
            numero_processo="1234567-12.2023.8.26.0001",
            titulo="RESPONSABILIDADE CIVIL. DANO MORAL.",
            conteudo="Conteúdo do julgado favorável",
            data_publicacao=date.today(),
            tribunal="TJSP",
            djen_id="TJSP123456",
            hash_conteudo="abc123",
            criado_por=self.user
        )
    
    def test_create_analise_tese(self):
        """Testa criação de análise de tese"""
        analise = AnaliseJurisprudenciaTese.objects.create(
            tese_juridica="Responsabilidade civil por danos morais em negativação indevida",
            termos_busca=["dano moral", "negativação", "Serasa"],
            filtros_aplicados={"tribunal": "TJSP", "periodo": "2023"},
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            total_julgados_encontrados=100,
            total_julgados_favoraveis=75,
            percentual_favorabilidade=Decimal('75.00'),
            argumentos_favoraveis=["Dano in re ipsa", "Valor moral"],
            precedentes_fortes=["STJ REsp 123456"],
            criado_por=self.user
        )
        
        self.assertEqual(analise.total_julgados_encontrados, 100)
        self.assertEqual(analise.percentual_favorabilidade, Decimal('75.00'))
        self.assertEqual(analise.status, 'processando')
        self.assertIn("Responsabilidade civil", str(analise))
    
    def test_add_julgado_favoravel(self):
        """Testa adição de julgado favorável com score"""
        analise = AnaliseJurisprudenciaTese.objects.create(
            tese_juridica="Teste de tese",
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            criado_por=self.user
        )
        
        julgado_favoravel = JulgadoFavoravel.objects.create(
            analise=analise,
            julgado=self.julgado,
            score_favorabilidade=Decimal('85.50'),
            justificativa="Julgado com argumentação sólida sobre dano moral",
            eh_precedente_forte=True,
            argumentos_chave=["dano in re ipsa", "quantum indenizatório"],
            criado_por=self.user
        )
        
        self.assertEqual(julgado_favoravel.score_favorabilidade, Decimal('85.50'))
        self.assertTrue(julgado_favoravel.eh_precedente_forte)
        self.assertIn("85.50", str(julgado_favoravel))


class AnaliseJurisprudenciaNeutraTestCase(TestCase):
    """Testes para o modelo AnaliseJurisprudenciaNeutra"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_analise_neutra(self):
        """Testa criação de análise neutra"""
        analise = AnaliseJurisprudenciaNeutra.objects.create(
            tema_juridico="Usucapião Extrajudicial",
            filtros_aplicados={"tribunal": "TJSP"},
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            total_julgados_analisados=200,
            julgados_favoraveis=120,
            julgados_contrarios=60,
            julgados_neutros=20,
            tendencia_majoritaria='favoravel',
            argumentos_pro=["Celeridade processual", "Economia judicial"],
            argumentos_contra=["Falta de contraditório", "Riscos jurídicos"],
            evolucao_temporal={"2023": {"favoravel": 60, "contrario": 30}},
            criado_por=self.user
        )
        
        self.assertEqual(analise.total_julgados_analisados, 200)
        self.assertEqual(analise.tendencia_majoritaria, 'favoravel')
        self.assertEqual(len(analise.argumentos_pro), 2)
        self.assertIn("Usucapião", str(analise))


class PadroesVaraTribunalTestCase(TestCase):
    """Testes para o modelo PadroesVaraTribunal"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_padroes_vara(self):
        """Testa criação de padrões de vara"""
        padroes = PadroesVaraTribunal.objects.create(
            tribunal="TJSP",
            vara="1ª Vara Cível de São Paulo",
            tema_juridico="Dano Moral em Acidente de Trânsito",
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            total_julgados_analisados=50,
            padroes_julgamento={
                "valor_medio_indenizacao": 15000,
                "tendencia": "conservadora"
            },
            perfil_julgador={"experiencia": "alta", "area_especializacao": "civil"},
            precedentes_citados=["STJ REsp 789123", "STF RE 456789"],
            valores_indenizacao={"min": 5000, "max": 30000, "media": 15000},
            teses_aceitas=["Dano moral in re ipsa"],
            teses_rejeitadas=["Dano moral por mero aborrecimento"],
            criado_por=self.user
        )
        
        self.assertEqual(padroes.tribunal, "TJSP")
        self.assertEqual(padroes.total_julgados_analisados, 50)
        self.assertEqual(padroes.padroes_julgamento["valor_medio_indenizacao"], 15000)
        self.assertIn("TJSP", str(padroes))
    
    def test_unique_together_constraint(self):
        """Testa constraint de unicidade"""
        PadroesVaraTribunal.objects.create(
            tribunal="TJSP",
            vara="1ª Vara Cível",
            tema_juridico="Teste",
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            criado_por=self.user
        )
        
        with self.assertRaises(IntegrityError):
            PadroesVaraTribunal.objects.create(
                tribunal="TJSP",
                vara="1ª Vara Cível",
                tema_juridico="Teste",
                periodo_analise_inicio=date(2023, 1, 1),
                periodo_analise_fim=date(2023, 12, 31),
                criado_por=self.user
            )


class EstrategiaAntecipatoriaTestCase(TestCase):
    """Testes para o modelo EstrategiaAntecipatoria"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.padrao_vara = PadroesVaraTribunal.objects.create(
            tribunal="TJSP",
            vara="1ª Vara Cível",
            tema_juridico="Responsabilidade Civil",
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            criado_por=self.user
        )
    
    def test_create_estrategia_antecipatoria(self):
        """Testa criação de estratégia antecipatória"""
        estrategia = EstrategiaAntecipatoria.objects.create(
            numero_processo="9876543-21.2024.8.26.0100",
            tribunal_destino="TJSP",
            vara_destino="1ª Vara Cível de São Paulo",
            documentos_caso=["inicial.pdf", "contestacao.pdf"],
            resumo_caso="Ação de indenização por danos morais e materiais",
            padrao_vara_relacionado=self.padrao_vara,
            probabilidade_sucesso=Decimal('78.50'),
            riscos_identificados=["Vara conservadora", "Precedente contrário"],
            estrategias_mitigacao=["Citar precedente favorável", "Enfatizar dano"],
            argumentos_direcionados=["Dano in re ipsa", "Responsabilidade objetiva"],
            precedentes_recomendados=["STJ REsp 123456"],
            pontos_atencao=["Quantum indenizatório", "Nexo causal"],
            cronograma_recomendado={"teplica": "15 dias", "audiencia": "30 dias"},
            criado_por=self.user
        )
        
        self.assertEqual(estrategia.probabilidade_sucesso, Decimal('78.50'))
        self.assertEqual(estrategia.tribunal_destino, "TJSP")
        self.assertEqual(estrategia.padrao_vara_relacionado, self.padrao_vara)
        self.assertEqual(len(estrategia.riscos_identificados), 2)
        self.assertIn("9876543", str(estrategia))
    
    def test_update_resultado_real(self):
        """Testa atualização com resultado real"""
        estrategia = EstrategiaAntecipatoria.objects.create(
            numero_processo="1111111-11.2024.8.26.0100",
            tribunal_destino="TJSP",
            resumo_caso="Teste de caso",
            probabilidade_sucesso=Decimal('80.00'),
            criado_por=self.user
        )
        
        # Simular resultado real
        estrategia.resultado_real = 'favoravel'
        estrategia.data_resultado = date.today()
        estrategia.observacoes_resultado = "Resultado conforme previsto"
        estrategia.save()
        
        self.assertEqual(estrategia.resultado_real, 'favoravel')
        self.assertEqual(estrategia.data_resultado, date.today())


class ModelsIntegrationTestCase(TestCase):
    """Testes de integração entre modelos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_complete_workflow(self):
        """Testa fluxo completo dos 4 cenários"""
        # 1. Criar julgados
        julgado1 = Julgado.objects.create(
            numero_processo="1111111-11.2023.8.26.0001",
            titulo="Julgado Favorável",
            conteudo="Conteúdo favorável à tese",
            data_publicacao=date.today(),
            tribunal="TJSP",
            djen_id="TJSP111",
            hash_conteudo="hash111",
            criado_por=self.user
        )
        
        julgado2 = Julgado.objects.create(
            numero_processo="2222222-22.2023.8.26.0002",
            titulo="Julgado Neutro",
            conteudo="Conteúdo neutro",
            data_publicacao=date.today(),
            tribunal="TJSP",
            djen_id="TJSP222",
            hash_conteudo="hash222",
            criado_por=self.user
        )
        
        # 2. Cenário 1: Análise de Tese
        analise_tese = AnaliseJurisprudenciaTese.objects.create(
            tese_juridica="Teste de integração",
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            criado_por=self.user
        )
        
        JulgadoFavoravel.objects.create(
            analise=analise_tese,
            julgado=julgado1,
            score_favorabilidade=Decimal('90.00'),
            justificativa="Altamente favorável",
            criado_por=self.user
        )
        
        # 3. Cenário 2: Análise Neutra
        analise_neutra = AnaliseJurisprudenciaNeutra.objects.create(
            tema_juridico="Teste de integração neutra",
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            tendencia_majoritaria='dividida',
            criado_por=self.user
        )
        analise_neutra.julgados_representativos.add(julgado1, julgado2)
        
        # 4. Cenário 3: Padrões de Vara
        padroes = PadroesVaraTribunal.objects.create(
            tribunal="TJSP",
            vara="1ª Vara Teste",
            tema_juridico="Integração",
            periodo_analise_inicio=date(2023, 1, 1),
            periodo_analise_fim=date(2023, 12, 31),
            criado_por=self.user
        )
        padroes.julgados_analisados.add(julgado1, julgado2)
        
        # 5. Cenário 4: Estratégia Antecipatória
        estrategia = EstrategiaAntecipatoria.objects.create(
            numero_processo="9999999-99.2024.8.26.0100",
            tribunal_destino="TJSP",
            resumo_caso="Caso de integração",
            padrao_vara_relacionado=padroes,
            probabilidade_sucesso=Decimal('85.00'),
            criado_por=self.user
        )
        
        # Verificações
        self.assertEqual(Julgado.objects.count(), 2)
        self.assertEqual(AnaliseJurisprudenciaTese.objects.count(), 1)
        self.assertEqual(JulgadoFavoravel.objects.count(), 1)
        self.assertEqual(AnaliseJurisprudenciaNeutra.objects.count(), 1)
        self.assertEqual(PadroesVaraTribunal.objects.count(), 1)
        self.assertEqual(EstrategiaAntecipatoria.objects.count(), 1)
        
        # Testar relacionamentos
        self.assertEqual(analise_tese.julgados_favoraveis.count(), 1)
        self.assertEqual(analise_neutra.julgados_representativos.count(), 2)
        self.assertEqual(padroes.julgados_analisados.count(), 2)
        self.assertEqual(estrategia.padrao_vara_relacionado, padroes)
