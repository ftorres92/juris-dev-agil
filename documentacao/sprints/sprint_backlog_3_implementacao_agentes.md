# 📋 Sprint Backlog - Sprint 3 - Implementação dos Agentes

## 🎯 **Objetivo do Sprint**
Implementar a infraestrutura base e o primeiro agente (AgenteClassificadorTese) conforme especificação técnica da Sprint 2, estabelecendo a base para os demais agentes.

## 📊 **Resumo do Sprint**
- **Sprint**: Sprint 3 - Implementação Base
- **Duração**: 2 semanas
- **Foco**: Infraestrutura e AgenteClassificadorTese
- **Total de Story Points**: 34 pontos

---

## 🏗️ **Tarefas Técnicas Prioritárias**

### **1. Configuração de Infraestrutura** 
**Responsável**: Fernando Torres (Líder Técnico)  
**Estimativa**: 8 pontos  
**Prioridade**: MUST HAVE  
**Status**: 🔄 Em Andamento

**Critérios de Aceite**:
- [ ] Redis configurado para cache e filas
- [ ] Celery configurado com filas dedicadas por agente
- [ ] ContextManager implementado para gestão de tokens
- [ ] Configuração de ambiente para Gemini 2.5 e OpenAI
- [ ] Logs estruturados JSON implementados
- [ ] Métricas Prometheus configuradas

**Tarefas Específicas**:
- [ ] Configurar Redis local e remoto
- [ ] Implementar Celery com filas `juris.classificador`, `juris.neutro`, `juris.vara`, `juris.estrategico`
- [ ] Criar ContextManager com limite de 12k tokens por agente
- [ ] Configurar Google AI SDK e OpenAI SDK
- [ ] Implementar sistema de logs estruturados
- [ ] Configurar métricas básicas

---

### **2. Integração DJEN - Cliente Avançado**
**Responsável**: Elinton Camacho (Pesquisador Científico)  
**Estimativa**: 8 pontos  
**Prioridade**: MUST HAVE  
**Status**: ⏳ Pendente

**Critérios de Aceite**:
- [ ] DJENCollector implementado com rate limiting (60 req/min)
- [ ] Cache Redis com TTL 24h funcionando
- [ ] Backoff exponencial para rate limits
- [ ] Chunking automático para grandes volumes
- [ ] Fallback strategy implementada
- [ ] Logs detalhados de uso e performance

**Tarefas Específicas**:
- [ ] Implementar DJENCollector com asyncio.Semaphore(60)
- [ ] Configurar cache Redis com chaves `djen:<tenant_id>:<hash_consulta>`
- [ ] Implementar backoff exponencial
- [ ] Criar sistema de chunking inteligente
- [ ] Implementar fallback para múltiplas tentativas
- [ ] Adicionar logs estruturados com job_id

---

### **3. AgenteClassificadorTese - Implementação**
**Responsável**: Flavio Eustaquio (Dev de Protótipos)  
**Estimativa**: 13 pontos  
**Prioridade**: MUST HAVE  
**Status**: ⏳ Pendente

**Critérios de Aceite**:
- [ ] AgenteClassificadorTese implementado com Gemini 2.5
- [ ] Processamento em batches de 20 julgados
- [ ] Fallback para GPT-4 em caso de falha
- [ ] Persistência em AnaliseJurisprudenciaTese
- [ ] Eventos `juris.analise_tese.ready` funcionando
- [ ] SLA de 3 minutos (p95) com até 500 julgados

**Tarefas Específicas**:
- [ ] Implementar classe AgenteClassificadorTese
- [ ] Configurar prompt base para classificação
- [ ] Implementar processamento em batches
- [ ] Criar sistema de fallback LLM
- [ ] Implementar persistência de resultados
- [ ] Configurar eventos e notificações
- [ ] Implementar testes de performance

---

### **4. API REST - Endpoints Básicos**
**Responsável**: Heloiza de Oliveira (Dev de Protótipos)  
**Estimativa**: 5 pontos  
**Prioridade**: MUST HAVE  
**Status**: ⏳ Pendente

**Critérios de Aceite**:
- [ ] Endpoint POST `/api/juris/tese/analises/` funcionando
- [ ] Endpoint GET `/api/juris/jobs/{id}/status/` funcionando
- [ ] Serializers Django REST Framework implementados
- [ ] Validação de payload implementada
- [ ] Documentação básica da API

**Tarefas Específicas**:
- [ ] Implementar AnaliseJurisprudenciaTeseRequest serializer
- [ ] Criar view para criação de análise
- [ ] Implementar view de status de job
- [ ] Configurar URLs da API
- [ ] Adicionar validações de entrada
- [ ] Criar documentação básica

---

## 👥 **Distribuição de Responsabilidades**

### **Fernando Torres** (Líder Técnico)
- ✅ Configuração de infraestrutura (Redis, Celery, ContextManager)
- ✅ Configuração de LLMs (Gemini, OpenAI)
- ✅ Sistema de logs e métricas
- 🔄 **Status**: Em andamento

### **Elinton Camacho** (Pesquisador Científico)
- ⏳ Integração DJEN avançada
- ⏳ Cliente com rate limiting
- ⏳ Sistema de cache
- 🔄 **Status**: Pendente

### **Flavio Eustaquio** (Dev de Protótipos)
- ⏳ AgenteClassificadorTese
- ⏳ Processamento com LLM
- ⏳ Sistema de fallback
- 🔄 **Status**: Pendente

### **Heloiza de Oliveira** (Dev de Protótipos)
- ⏳ API REST endpoints
- ⏳ Serializers e validações
- ⏳ Documentação da API
- 🔄 **Status**: Pendente

### **José Ramos** (Dev de Protótipos)
- ⏳ Testes unitários dos agentes
- ⏳ Testes de integração
- ⏳ Testes de performance
- 🔄 **Status**: Pendente

---

## 🚀 **Entregas Esperadas para Sprint 3**

### **Entregas Técnicas**:
1. **Infraestrutura completa** (Fernando)
2. **Cliente DJEN avançado** (Elinton)
3. **AgenteClassificadorTese funcionando** (Flavio)
4. **API REST básica** (Heloiza)
5. **Testes implementados** (José)

### **Entregas de Documentação**:
1. **Especificação técnica validada** ✅
2. **Documentação da API** 
3. **Guia de configuração**
4. **Manual de troubleshooting**

---

## 📊 **Métricas de Sucesso**

### **Técnicas**:
- [ ] AgenteClassificadorTese processando julgados em < 3 minutos
- [ ] Precisão ≥ 90% na classificação favorável/desfavorável
- [ ] Cache Redis funcionando com TTL 24h
- [ ] Rate limiting DJEN respeitado (60 req/min)
- [ ] Fallback LLM funcionando

### **Processo**:
- [ ] Todas as tarefas atribuídas
- [ ] Daily Scrum realizados
- [ ] Progresso documentado no GitHub
- [ ] Code reviews realizados
- [ ] Testes passando

---

## 🚧 **Riscos Identificados**

1. **Rate Limiting DJEN**: Limite de 60 req/min pode ser restritivo
   - **Mitigação**: Cache agressivo + backoff exponencial

2. **Custos LLM**: Gemini 2.5 e GPT-4 podem ser caros
   - **Mitigação**: ContextManager + chunking inteligente

3. **Performance**: Processamento de 500 julgados pode ser lento
   - **Mitigação**: Processamento paralelo + otimizações

4. **Precisão**: Classificação pode não atingir 90%
   - **Mitigação**: Ajustes de prompt + validação com dataset

---

## 📅 **Cronograma da Sprint**

### **Semana 1**
- **Segunda**: Configuração infraestrutura (Fernando)
- **Terça**: Integração DJEN (Elinton)
- **Quarta**: Início AgenteClassificadorTese (Flavio)
- **Quinta**: API REST (Heloiza)
- **Sexta**: Testes e integração (José)

### **Semana 2**
- **Segunda**: Finalização AgenteClassificadorTese
- **Terça**: Integração completa
- **Quarta**: Testes de performance
- **Quinta**: Documentação e ajustes
- **Sexta**: Review e planejamento Sprint 4

---

## 🎯 **Definition of Done (DoD)**

Uma tarefa está pronta quando:
- [ ] Código implementado e funcionando
- [ ] Testes unitários passando
- [ ] Testes de integração passando
- [ ] Documentação atualizada
- [ ] Code review realizado
- [ ] Commit no repositório
- [ ] Métricas de performance validadas

---

## 📋 **Próximas Sprints**

### **Sprint 4**: AgenteAnalisadorNeutro
- Implementação do segundo agente
- Dashboard de análise neutra
- Interface de visualização

### **Sprint 5**: AgenteAnalisadorVara
- Implementação do terceiro agente
- Análise de padrões por vara
- Comparativo entre órgãos

### **Sprint 6**: AgenteEstrategicoAntecipatorio
- Implementação do quarto agente
- Predição de resultados
- Estratégias personalizadas

---

**Criado em**: 05/01/2025  
**Responsável**: Fernando Torres  
**Próxima revisão**: 12/01/2025
