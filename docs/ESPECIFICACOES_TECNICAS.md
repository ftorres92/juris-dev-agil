# 🔧 Especificações Técnicas - Pesquisador de Jurisprudência DJEN

## 🏗️ **Arquitetura Técnica**

### **Framework Base**
- **Django 4.x**: Framework principal para backend
- **PostgreSQL**: Banco de dados para persistência
- **Redis**: Cache e filas para processamento assíncrono
- **Celery**: Processamento de tarefas em background

### **Agentes de IA**
- **Biblioteca Principal**: **CrewAI** ou **Google AI SDK** para orquestração de agentes
- **Alternativa**: **Agno** para criação de agentes especializados
- **LLM Padrão**: **Google Gemini 2.5** (principal)
- **LLM Fallback**: **OpenAI GPT-4** (backup)

### **Integração DJEN**
- **API Gratuita**: Uso das rotas públicas do DJEN
- **Rate Limiting**: 60 requests/min (uso polite)
- **Cache Inteligente**: Redis para evitar soft ban
- **Retry Logic**: Backoff exponencial para falhas

## 🤖 **Agentes Especializados por Cenário**

### **🔍 Cenário 1: AgenteClassificadorTese**
```python
class AgenteClassificadorTese:
    """
    Responsabilidades:
    - Receber julgados do DJEN via pesquisa por termo
    - Classificar cada julgado como favorável/desfavorável à tese
    - Calcular score de favorabilidade (0-100%)
    - Identificar precedentes fortes (STJ, STF)
    """
    
    def __init__(self):
        self.llm_primary = GeminiLLM()
        self.llm_fallback = OpenAILLM()
        self.context_manager = ContextManager(max_tokens=8000)
    
    def classificar_por_tese(self, julgados, tese_cliente):
        # Implementação com chunking para evitar estouro de contexto
        pass
```

### **📊 Cenário 2: AgenteAnalisadorNeutro**
```python
class AgenteAnalisadorNeutro:
    """
    Responsabilidades:
    - Analisar jurisprudência de forma neutra e objetiva
    - Calcular entendimento majoritário sem viés
    - Identificar argumentos pró e contra
    - Gerar relatório objetivo
    """
    
    def analisar_jurisprudencia_neutra(self, julgados):
        # Processamento em batches para grandes volumes
        pass
```

### **🏛️ Cenário 3: AgenteAnalisadorVara**
```python
class AgenteAnalisadorVara:
    """
    Responsabilidades:
    - Filtrar julgados por vara/tribunal específico
    - Identificar padrões de julgamento por tema
    - Gerar perfil do órgão julgador
    - Criar relatório: "Sobre tema X, essa vara decide..."
    """
    
    def analisar_padroes_vara(self, vara_tribunal, tema):
        # Análise específica por órgão julgador
        pass
```

### **🎯 Cenário 4: AgenteEstrategicoAntecipatorio**
```python
class AgenteEstrategicoAntecipatorio:
    """
    Responsabilidades:
    - Analisar histórico da vara/tribunal
    - Predizer como julgará caso específico
    - Calcular probabilidade de sucesso
    - Gerar estratégia personalizada
    """
    
    def analisar_estrategia_antecipatoria(self, caso, vara):
        # Predição baseada em padrões históricos
        pass
```

## 📊 **Modelos de Dados Django**

### **AnaliseJurisprudenciaTese**
```python
class AnaliseJurisprudenciaTese(models.Model):
    """Classificação por favorabilidade à tese"""
    tese_cliente = models.TextField()
    julgados_favoraveis = models.JSONField()
    julgados_desfavoraveis = models.JSONField() 
    score_favorabilidade = models.FloatField()  # 0-100%
    precedentes_fortes = models.JSONField()
    data_analise = models.DateTimeField(auto_now_add=True)
```

### **AnaliseJurisprudenciaNeutra**
```python
class AnaliseJurisprudenciaNeutra(models.Model):
    """Análise neutra sem viés"""
    tema_juridico = models.CharField(max_length=200)
    entendimento_majoritario = models.TextField()
    argumentos_pro = models.JSONField()
    argumentos_contra = models.JSONField()
    tendencia_geral = models.CharField(max_length=50)
```

### **PadroesVaraTribunal**
```python
class PadroesVaraTribunal(models.Model):
    """Padrões por vara/tribunal específico"""
    vara_tribunal = models.CharField(max_length=200)
    tema_juridico = models.CharField(max_length=200)
    perfil_julgador = models.JSONField()
    padroes_tema = models.JSONField()
    recomendacoes_estrategicas = models.TextField()
```

### **EstrategiaAntecipatoria**
```python
class EstrategiaAntecipatoria(models.Model):
    """Predições estratégicas"""
    vara_tribunal = models.CharField(max_length=200)
    probabilidade_sucesso = models.FloatField()
    riscos_identificados = models.JSONField()
    estrategia_personalizada = models.TextField()
    argumentos_direcionados = models.JSONField()
```

## ⚠️ **Considerações Técnicas Críticas**

### **1. Gestão de Contexto (Limite de Tokens)**
- **Problema**: DJEN pode retornar muitos julgados, estourando contexto
- **Solução**: Chunking inteligente em batches de 50-100 julgados
- **Implementação**: `ContextManager` para monitorar e dividir contexto

```python
class ContextManager:
    def __init__(self, max_tokens=8000):
        self.max_tokens = max_tokens
    
    def chunk_julgados(self, julgados, tese):
        # Divide julgados em chunks que cabem no contexto
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for julgado in julgados:
            tokens = self.count_tokens(julgado + tese)
            if current_tokens + tokens > self.max_tokens:
                chunks.append(current_chunk)
                current_chunk = [julgado]
                current_tokens = tokens
            else:
                current_chunk.append(julgado)
                current_tokens += tokens
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
```

### **2. Uso Polite do DJEN**
- **Rate Limiting**: 60 req/min máximo
- **Cache Redis**: 24h para consultas similares
- **Backoff**: Exponencial em caso de rate limit
- **Monitoramento**: Logs detalhados de uso

```python
class DJENClient:
    def __init__(self):
        self.rate_limiter = RateLimiter(60, 60)  # 60 req/min
        self.cache = RedisCache(ttl=86400)  # 24h
    
    def buscar_julgados(self, termo, vara=None):
        cache_key = f"djen:{hash(termo)}:{vara}"
        
        # Verificar cache primeiro
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Rate limiting
        self.rate_limiter.wait()
        
        # Fazer request com retry
        try:
            response = self._request_with_retry(termo, vara)
            self.cache.set(cache_key, response)
            return response
        except RateLimitError:
            # Backoff exponencial
            time.sleep(120)  # 2 min
            return self.buscar_julgados(termo, vara)
```

### **3. Pipeline de Processamento**
```
DJEN → Cache → Chunking → Agente → Análise → Cache → UI
```

### **4. Fallback Strategy**
- **Gemini OK**: Usar Gemini 2.5
- **Gemini Fail**: Fallback para OpenAI GPT-4
- **Ambos Fail**: Enfileirar para retry posterior

## 🚀 **Implementação por Sprint**

### **Sprint 3 - MVP (Cenário 1)**
- ✅ Integração DJEN com rate limiting
- ✅ AgenteClassificadorTese com Gemini
- ✅ ContextManager para chunking
- ✅ Cache Redis básico
- ✅ Interface para busca favorável

### **Sprint 4 - Cenário 2**
- ✅ AgenteAnalisadorNeutro
- ✅ Dashboard com visualizações
- ✅ Fallback para OpenAI

### **Sprint 5 - Cenário 3**
- ✅ AgenteAnalisadorVara
- ✅ Análise de padrões por órgão
- ✅ Interface de comparação

### **Sprint 6 - Cenário 4**
- ✅ AgenteEstrategicoAntecipatorio
- ✅ Predições baseadas em ML
- ✅ Performance optimization

## 📋 **Dependências Técnicas**

### **Python Packages**
```
# requirements.txt
django==4.2.0
psycopg2-binary==2.9.7
redis==4.6.0
celery==5.3.1
google-generativeai==0.2.0
openai==1.3.0
crewai==0.1.0  # ou agno
pandas==2.0.3
numpy==1.24.3
```

### **Variáveis de Ambiente**
```
# .env
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_fallback_key
DJEN_BASE_URL=https://djen.api.url
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost/db
```

---

**Esta especificação técnica garante que o sistema seja robusto, eficiente e respeite os limites do DJEN, implementando os 4 cenários estratégicos com a arquitetura Django + Agentes + Gemini conforme sua visão.**
