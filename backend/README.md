# 🏗️ Backend - Agentes para Análise de Jurisprudência Estratégica

Este diretório contém a aplicação backend do sistema de agentes de IA para análise de jurisprudência.

## 🎯 **Objetivo**

Implementar o backend Django com agentes especializados para análise de jurisprudência, integração com DJEN e processamento de dados jurídicos.

## 🏗️ **Arquitetura Backend**

### **Framework Base**
- **Django 4.2.7**: Framework principal ✅
- **SQLite**: Banco de dados para desenvolvimento ✅
- **Redis**: Cache configurado (não implementado ainda)
- **Celery**: Planejado para futuras implementações

### **Agentes de IA**
- **NeutralSearchAgent**: Implementado e funcionando ✅
- **Google Gemini 2.5**: Dependência instalada (não implementado)
- **OpenAI GPT-4**: Dependência instalada (não implementado)

### **Integração DJEN**
- **API Gratuita**: Uso das rotas públicas do DJEN ✅
- **Rate Limiting**: 60 requests/min (uso polite) ✅
- **Cache Inteligente**: Redis configurado (não implementado)
- **Retry/Backoff**: Exponencial implementado ✅
- **Sanitização HTML**: Bleach implementado ✅

## 🤖 **Agentes Especializados**

### **Cenário 1: AgenteClassificadorTese**
- Classifica julgados favoráveis/desfavoráveis à tese
- Score de favorabilidade (0-100%)
- Identificação de precedentes fortes

### **Cenário 2: AgenteAnalisadorNeutro** ✅ **IMPLEMENTADO**
- Análise neutra da jurisprudência sem viés ✅
- Identificação de argumentos pró e contra ✅
- Entendimento majoritário ✅
- **NeutralSearchAgent**: Gera variações automáticas de busca ✅
- **Sinônimos jurídicos**: Substituição inteligente de termos ✅
- **Agregação**: Deduplicação e ranking por relevância ✅

### **Cenário 3: AgenteAnalisadorVara**
- Análise de padrões por vara/tribunal específico
- Perfil do julgador
- Relatórios personalizados

### **Cenário 4: AgenteEstrategicoAntecipatorio**
- Predição de como vara julgará o caso
- Probabilidade de sucesso
- Estratégia personalizada

## 📊 **Modelos de Dados** ✅ **IMPLEMENTADOS**

- **Julgado**: Base de julgados coletados do DJEN ✅
- **AnaliseJurisprudenciaTese**: Classificação por favorabilidade ✅
- **AnaliseJurisprudenciaNeutra**: Análise neutra sem viés ✅
- **PadroesVaraTribunal**: Padrões por órgão específico ✅
- **EstrategiaAntecipatoria**: Predições estratégicas ✅
- **JulgadoFavoravel**: Relacionamento com scores ✅

## 🚀 **Status de Implementação**

- ✅ **Sprint 2**: Interface Django + Integração DJEN (CONCLUÍDA)
- ✅ **Sprint 3**: Validação e Melhorias (CONCLUÍDA)
- ✅ **Agente Neutro**: NeutralSearchAgent (IMPLEMENTADO)
- ⏳ **Sprint 4**: AgenteClassificadorTese (PLANEJADO)
- ⏳ **Sprint 5**: AgenteAnalisadorVara (PLANEJADO)
- ⏳ **Sprint 6**: AgenteEstrategicoAntecipatorio (PLANEJADO)

## 📋 **Próximos Passos**

1. ✅ Configurar ambiente Django
2. ✅ Implementar modelos de dados
3. ✅ Integrar com DJEN
4. ✅ Implementar Agente Neutro
5. 🔄 Implementar AgenteClassificadorTese
6. 🔄 Implementar AgenteAnalisadorVara
7. 🔄 Implementar AgenteEstrategicoAntecipatorio
8. 🔄 Implementar cache Redis
9. 🔄 Configurar Celery para processamento assíncrono

## 🌐 **Interface Sprint 2 · DJEN**

- `GET /buscar/` e `GET /djen/consulta/`: página Django (Bootstrap) para pesquisa de termos no DJEN
- Campos suportados: termo, tribunais múltiplos (STF/STJ/TSE/TST/STM, TRFs, TRTs, TREs, TJs, TJMs), período, limite, número do processo
- Integração real com `DJEN_API_URL` (retry/backoff) + sanitização de HTML (bleach)
- Pós-filtragem semântica local: frases, AND/OR/NOT, normalização acento-insensível, stopwords PT, destaque `<mark>` e ranking por relevância/recência
- **Status**: ✅ Implementada e funcional

## 🎨 **Interface Django (Sprint 3+)**

### **Arquitetura Frontend Django**
- **Django Templates**: Sistema de templates nativo
- **Bootstrap 5**: Framework CSS responsivo
- **Chart.js**: Visualização de dados
- **HTMX**: Interatividade sem JavaScript complexo
- **Django REST Framework**: API para integrações futuras

### **Páginas Planejadas**
- **Dashboard**: Visão geral das análises e métricas
- **ConsultaJurisprudencia**: Interface de busca aprimorada
- **ResultadosAnalise**: Visualização de resultados dos agentes
- **GraficosEstatisticos**: Charts e métricas interativas
- **ExportacaoRelatorios**: Geração e download de PDFs

### **Melhorias Django**
- **Templates Responsivos**: Design mobile-first
- **Componentes Reutilizáveis**: Base templates e includes
- **API REST**: Endpoints para futuras integrações
- **WebSocket**: Atualizações em tempo real (Django Channels)

## 🧪 **Evidências de Funcionamento**

### **Testes Automatizados**
```bash
$ python manage.py test --verbosity=2
Ran 17 tests in 1.068s
OK
```

### **Integração DJEN**
```bash
🧪 Testando integração DJEN...
✅ Status: djen
✅ Tempo: 1639 ms
✅ Quantidade: 5 julgados
✅ Primeiro resultado: TJSP
```

### **Agente Neutro**
```bash
🤖 Testando Agente Neutro...
✅ Origem: agente_neutro
✅ Tempo total: 2950 ms
✅ Quantidade: 3 julgados
✅ Variações: 3
  1. danos morais - Termo informado pelo usuário
  2. "danos morais" - Prioriza a frase exata
  3. prejuizos morais - Inclui sinônimos jurídicos relevantes
```

## 🚀 **Como Executar**

### **Configuração do Ambiente**
```bash
# Navegar para o diretório
cd /Users/fernandotorres/Juris-Dev-agil/backend

# Ativar ambiente virtual
source ../venv/bin/activate

# Executar migrações
python manage.py migrate

# Executar testes
python manage.py test

# Iniciar servidor
python manage.py runserver 8000
```

### **URLs Disponíveis**
- `http://localhost:8000/` - Página inicial
- `http://localhost:8000/buscar/` - Busca de jurisprudência
- `http://localhost:8000/djen/consulta/` - Consulta DJEN

### **Testar Integração DJEN**
```bash
python -c "
from jurisprudencia.utils.djen_api import buscar_jurisprudencia_por_termo
resultado = buscar_jurisprudencia_por_termo({
    'termo': 'responsabilidade civil',
    'tribunais': ['TJSP'],
    'limite': 5
})
print(f'Status: {resultado.get(\"origem\")}')
print(f'Tempo: {resultado.get(\"tempoExecucaoMs\")} ms')
print(f'Quantidade: {resultado.get(\"quantidade\")} julgados')
"
```

### **Testar Agente Neutro**
```bash
python -c "
from jurisprudencia.utils.neutral_agent import executar_busca_neutra
resultado = executar_busca_neutra({
    'termo': 'danos morais',
    'tribunais': ['TJSP'],
    'limite': 3
})
print(f'Origem: {resultado.get(\"origem\")}')
print(f'Tempo: {resultado.get(\"tempoExecucaoMs\")} ms')
print(f'Variações: {len(resultado.get(\"variacoes\", []))}')
"
```
