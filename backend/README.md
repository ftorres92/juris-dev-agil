# 🏗️ Backend - Agentes para Análise de Jurisprudência Estratégica

Este diretório contém a aplicação backend do sistema de agentes de IA para análise de jurisprudência.

## 🎯 **Objetivo**

Implementar o backend Django com agentes especializados para análise de jurisprudência, integração com DJEN e processamento de dados jurídicos.

## 🏗️ **Arquitetura Backend**

### **Framework Base**
- **Django 4.x**: Framework principal
- **PostgreSQL**: Banco de dados para persistência
- **Redis**: Cache e filas para processamento assíncrono
- **Celery**: Processamento de tarefas em background

### **Agentes de IA**
- **CrewAI**: Orquestração de agentes
- **Google Gemini 2.5**: LLM principal
- **OpenAI GPT-4**: LLM fallback

### **Integração DJEN**
- **API Gratuita**: Uso das rotas públicas do DJEN
- **Rate Limiting**: 60 requests/min (uso polite)
- **Cache Inteligente**: Redis para evitar soft ban

## 🤖 **Agentes Especializados**

### **Cenário 1: AgenteClassificadorTese**
- Classifica julgados favoráveis/desfavoráveis à tese
- Score de favorabilidade (0-100%)
- Identificação de precedentes fortes

### **Cenário 2: AgenteAnalisadorNeutro**
- Análise neutra da jurisprudência sem viés
- Identificação de argumentos pró e contra
- Entendimento majoritário

### **Cenário 3: AgenteAnalisadorVara**
- Análise de padrões por vara/tribunal específico
- Perfil do julgador
- Relatórios personalizados

### **Cenário 4: AgenteEstrategicoAntecipatorio**
- Predição de como vara julgará o caso
- Probabilidade de sucesso
- Estratégia personalizada

## 📊 **Modelos de Dados**

- **AnaliseJurisprudenciaTese**: Classificação por favorabilidade
- **AnaliseJurisprudenciaNeutra**: Análise neutra sem viés
- **PadroesVaraTribunal**: Padrões por órgão específico
- **EstrategiaAntecipatoria**: Predições estratégicas

## 🚀 **Status de Implementação**

- 🔄 **Sprint 3**: MVP - Cenário 1 (Busca Favorável à Tese)
- ⏳ **Sprint 4**: Cenário 2 (Análise Neutra)
- ⏳ **Sprint 5**: Cenário 3 (Padrões por Vara)
- ⏳ **Sprint 6**: Cenário 4 (Estratégia Antecipatória)

## 📋 **Próximos Passos**

1. Configurar ambiente Django
2. Implementar modelos de dados
3. Desenvolver agentes especializados
4. Integrar com DJEN
5. Implementar cache Redis

## 🌐 **Interface Sprint 2 · DJEN**

- `GET /djen/consulta/`: página Django (Bootstrap) para pesquisa de termos diretamente no coletor DJEN
- Campos suportados: termo, tribunais múltiplos, tipo de decisão, período, limite de resultados
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
