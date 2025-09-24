# 📘 Especificação Técnica Sprint 2 - Agentes de Jurisprudência

> **Referência da Issue:** [#16](https://github.com/ftorres92/Juris-Dev-agil/issues/16)
> **Escopo do Sprint:** Definir especificações detalhadas dos agentes IA, interfaces, fluxos e dependências para habilitar a implementação técnica.

---

## 1. Objetivo

Consolidar as especificações funcionais e técnicas dos quatro agentes previstos para a análise estratégica de jurisprudência, estabelecendo contratos de integração, fluxos end-to-end, critérios de pronta-entrega e dependências. Este documento é a fonte de verdade para a Sprint 2 e orienta o trabalho das squads de backend, IA e produto.


## 2. Visão Geral dos Agentes

| Agente | Função Primária | Principais Modelos Django | Consumidores | Dependências Críticas |
| --- | --- | --- | --- | --- |
| `AgenteClassificadorTese` | Classificar julgados favoráveis/desfavoráveis e explicar decisão | `AnaliseJurisprudenciaTese`, `JulgadoFavoravel` | Dashboard de busca favorável, exportações | DJEN Collector, LLM Gemini, Redis cache |
| `AgenteAnalisadorNeutro` | Produzir visão neutra (pró/contra/neutro) e argumentos predominantes | `AnaliseJurisprudenciaNeutra` | Dashboard neutro, relatórios comparativos | DJEN Collector, LLM Gemini, agregador estatístico |
| `AgenteAnalisadorVara` | Mapear padrões históricos por vara/órgão | `PadroesVaraTribunal` | Dashboard padrões, Estratégico Antecipatório | DJEN Collector, Redis histórico, LLM Gemini |
| `AgenteEstrategicoAntecipatorio` | Calcular probabilidade de sucesso e recomendar estratégia | `EstrategiaAntecipatoria` | Dashboard estratégico, alertas caso | `PadroesVaraTribunal`, LLM Gemini, Regras heurísticas |


## 3. Requisitos Transversais

- **Orquestração**: Tarefas Celery com filas dedicadas (`juris.classificador`, `juris.neutro`, `juris.vara`, `juris.estrategico`).
- **Gestão de Contexto**: `ContextManager` limita tokens por agente (alvo 12k tokens) e aplica chunking de julgados.
- **Persistência**: Django ORM; transações atômicas em cada job para consistência.
- **Cache/Rate Limiting**: Redis armazena consultas recentes ao DJEN (TTL 24h) e checkpoints de processing.
- **Fallback LLM**: Fluxo primário usa Gemini 2.5; em falha ou latência > 20s, reexecuta com GPT-4 (máx. 1 retry).
- **Observabilidade**: Logs estruturados JSON (logger `juris.agentes`), métricas Prometheus (latência, erros, tokens), rastreio com `job_id` UUID.
- **Segurança**: Sanitização de dados sensíveis (hashing de números de processo nos logs), isolamento multi-tenant por `tenant_id` nas requisições.


## 4. Requisitos Não Funcionais

- **Precisão**: ≥ 90% para classificação favorável/desfavorável; ≥ 85% para tendências neutras; meta validada via dataset rotulado.
- **Performance**: SLA 3 minutos por job (p95) com até 500 julgados.
- **Disponibilidade**: Filas redundantes; reprocessamento automático em caso de falha.
- **Auditabilidade**: Logs e outputs armazenados com timestamp, modelo LLM utilizado, prompts e respostas truncadas.
- **Escalabilidade**: Processamento paralelo por tenant; limites de 3 jobs simultâneos por tenant para evitar rate limit DJEN.


## 5. Especificações por Agente

### 5.1 AgenteClassificadorTese

**Objetivo:** identificar julgados favoráveis e contrários a uma tese específica, com justificativa detalhada.

**Entradas (payload Celery `classificador_tese.run`):**
```json
{
  "analise_id": "UUID",
  "tenant_id": "UUID",
  "tese_juridica": "string",
  "termos_busca": ["string"],
  "filtros": {
    "tribunais": ["STJ", "TRF-3"],
    "periodo": {"inicio": "2022-01-01", "fim": "2024-12-31"},
    "areas": ["cível"],
    "outras_restricoes": {}
  },
  "limite_julgados": 500
}
```

**Fluxo Interno:**
1. Verificar cache Redis para chave `djen:<tenant_id>:<hash_consulta>`.
2. Se cache vazio, chamar `DJENCollector.search()` com backoff (taxa 60 req/min).
3. Pré-processar julgados (normalização, chunking em blocos ≤ 6k tokens).
4. Montar prompt do LLM por julgado, incluindo tese e critérios; processar em batches de 20.
5. Persistir resultados em `JulgadoFavoravel`, atualizar `AnaliseJurisprudenciaTese` (contagens, percentuais, argumentos).
6. Marcar `processado=True` nos `Julgado` utilizados e liberar evento `juris.analise_tese.ready`.

**Saídas:**
- Atualização de `AnaliseJurisprudenciaTese` com campos preenchidos.
- Event log `classificador_tese.completed` contendo métricas (latência, modelo, tokens).

**LLM Prompt Base:**
```
Você é um assistente jurídico especializado. Analise o trecho do julgado e classifique em {favorável, desfavorável, neutro} à tese abaixo.
Tese: {{tese_juridica}}
Critérios de avaliação: {{criterios}}
Responda em JSON com campos: classificacao, score (0-100), justificativa, argumentos_chave, precedentes.
```

**Dependências:** Gemini 2.5 (primary), GPT-4 (fallback), DJEN API, Redis, ContextManager.

**Falhas e Reações:**
- Timeout DJEN → reintentar até 3 vezes; se falha final, job aborta e status `erro`.
- Exceção LLM → fallback GPT-4; se persistir, logar erro crítico e marcar julgado como `pendente` para reprocessamento manual.

**Métricas:** precisão (via dataset), latência, contagem de julgados processados, percentual de fallback.

---

### 5.2 AgenteAnalisadorNeutro

**Objetivo:** fornecer visão neutra do tema, destacando argumentos pró e contra.

**Entradas (`analisador_neutro.run`):**
```json
{
  "analise_id": "UUID",
  "tenant_id": "UUID",
  "tema_juridico": "string",
  "periodo": {"inicio": "2023-01-01", "fim": "2024-12-31"},
  "filtros": {
    "tribunais": ["STJ", "STF"],
    "areas": ["constitucional"],
    "outras_restricoes": {}
  },
  "limite_julgados": 700
}
```

**Fluxo Interno:**
1. Obter corpus de julgados (cache + DJEN). Se conjunto > 700, aplicar amostragem estratificada por tribunal/data.
2. Clusterização leve (TF-IDF + KMeans/embedding) para agrupar temas.
3. Para cada cluster representativo, gerar resumo pró/contra via LLM.
4. Consolidar contagens, tendência (`favorável`, `contrária`, `dividida`, `neutra`).
5. Persistir métricas em `AnaliseJurisprudenciaNeutra` e relacionar `julgados_representativos`.

**Saídas:**
- Dados quantitativos e qualitativos preenchidos no modelo.
- Event `analisador_neutro.completed` com resumo das contagens e top argumentos.

**Prompt Base:**
```
Analise o conjunto de excertos fornecidos sobre "{{tema}}". Classifique o posicionamento predominante e liste:
1. Argumentos pró
2. Argumentos contra
3. Elementos neutros ou divididos
Responda em JSON.
```

**Dependências:** Gemini 2.5, embeddings (Gemini ou Vertex), Redis para cache de clusters, calculadora estatística (scikit-learn opcional).

**Métricas:** Erro absoluto médio da tendência vs dataset, tempo de processamento, diversidade de argumentos.

---

### 5.3 AgenteAnalisadorVara

**Objetivo:** mapear padrões decisórios por vara/órgão julgador.

**Entradas (`analisador_vara.run`):**
```json
{
  "padrao_id": "UUID",
  "tenant_id": "UUID",
  "tribunal": "string",
  "vara": "string",
  "tema_juridico": "string",
  "periodo": {"inicio": "2021-01-01", "fim": "2024-12-31"}
}
```

**Fluxo Interno:**
1. Recolher julgados filtrados por tribunal/vara/tema.
2. Extrair features estruturais (valores de indenização, partes, resultado).
3. Aplicar estatísticas descritivas + LLM para sintetizar padrões qualitativos.
4. Construir comparativo com outros órgãos (via base agregada por tribunal).
5. Persistir informações em `PadroesVaraTribunal` e vincular `julgados_analisados`.
6. Publicar evento `padrao_vara.updated` para consumo do Agente Estratégico.

**Dependências:** DJEN Collector, histórico de julgados persistidos, módulo estatístico (pandas), LLM Gemini.

**Métricas:** cobertura (nº julgados), acurácia valores médios vs base real, latência.

---

### 5.4 AgenteEstrategicoAntecipatorio

**Objetivo:** antecipar resultado provável de um caso específico e recomendar estratégia.

**Entradas (`estrategico_antecipatorio.run`):**
```json
{
  "estrategia_id": "UUID",
  "tenant_id": "UUID",
  "numero_processo": "string",
  "tribunal_destino": "string",
  "vara_destino": "string",
  "resumo_caso": "string",
  "documentos_caso": [{"tipo": "petição", "conteudo": "..."}]
}
```

**Fluxo Interno:**
1. Buscar `PadroesVaraTribunal` correspondente; se inexistente, acionar `analisador_vara.run` síncrono ou fallback geral do tribunal.
2. Extrair fatores relevantes do caso (temas, pedidos, provas) via LLM extractor.
3. Cruzar fatores com padrões históricos para calcular `probabilidade_sucesso` (regressão logística simples + ajuste heurístico do LLM).
4. Gerar recomendações (riscos, argumentos, precedentes) com base no histórico.
5. Persistir resultado em `EstrategiaAntecipatoria` e anexar relacionamentos.
6. Emitir evento `estrategia_antecipatoria.completed` para dashboards e alertas.

**Dependências:** `PadroesVaraTribunal`, Gemini 2.5, biblioteca estatística (`scikit-learn` opcional), heurísticas definidas pelo time jurídico.

**Métricas:** erro de previsão quando resultado real disponível, percentual de recomendações acionáveis, latência.


## 6. Interfaces e Contratos

### 6.1 API REST (a ser implementada)

| Endpoint | Método | Descrição | Agente | Payload Principal |
| --- | --- | --- | --- | --- |
| `/api/juris/tese/analises/` | POST | Cria nova análise favorável à tese | Classificador | `AnaliseJurisprudenciaTeseRequest` |
| `/api/juris/neutro/analises/` | POST | Solicita análise neutra | Analisador Neutro | `AnaliseNeutraRequest` |
| `/api/juris/vara/padroes/` | POST | Solicita mapeamento de padrões | Analisador Vara | `PadraoVaraRequest` |
| `/api/juris/estrategias/` | POST | Solicita estratégia antecipatória | Estratégico | `EstrategiaRequest` |
| `/api/juris/jobs/{id}/status/` | GET | Consulta status da tarefa | Todos | `job_id` |

### 6.2 Contratos de Evento (Message Bus)

- `juris.analise_tese.ready`
  - Campos: `analise_id`, `tenant_id`, `total_julgados`, `perc_favorabilidade`.

- `juris.analisador_neutro.completed`
  - Campos: `analise_id`, `tendencia_majoritaria`, `contador_pro`, `contador_contra`, `contador_neutro`.

- `juris.padrao_vara.updated`
  - Campos: `padrao_id`, `tribunal`, `vara`, `tema`, `timestamp`.

- `juris.estrategia.completed`
  - Campos: `estrategia_id`, `probabilidade_sucesso`, `principais_riscos`.

Todos os eventos compartilham header com `job_id`, `tenant_id`, `modelo_llm`, `duracao_ms`.


### 6.3 Repositório DJEN

- Interface `DJENCollector` (Python) expõe:
  - `search(tenant_id, filtros) -> List[Julgado]`
  - `fetch_by_ids(tenant_id, ids) -> List[Julgado]`
  - Rate limit interno com `asyncio.Semaphore(60)`.

- Resultado padronizado:
```json
{
  "djen_id": "string",
  "numero_processo": "string",
  "tribunal": "string",
  "vara": "string|null",
  "relator": "string|null",
  "data_publicacao": "YYYY-MM-DD",
  "ementa": "string",
  "inteiro_teor": "string",
  "url": "string"
}
```


## 7. Fluxos End-to-End

1. **Análise Favorável à Tese**
   1. Usuário cria requisição via API.
   2. `AnaliseJurisprudenciaTese` é criada com `status=processando`.
   3. Celery enfileira job `classificador_tese.run`.
   4. Job busca dados (cache + DJEN), processa com LLM, persiste resultados.
   5. Evento `juris.analise_tese.ready` dispara atualização de dashboard e notificação.

2. **Análise Neutra**
   1. API `POST /neutro` cria registro e job.
   2. Job clusteriza julgados, gera estatísticas, salva e emite evento.

3. **Padrões por Vara**
   1. Solicitação cria `PadroesVaraTribunal` (status processando).
   2. Job coleta histórico, aplica estatísticas, salva padrões, emite evento.

4. **Estratégia Antecipatória**
   1. Usuário envia caso e documentos.
   2. Job verifica se existe padrão de vara; se não, dispara job `analisador_vara` síncrono.
   3. Calcula probabilidade, recomenda estratégia, persiste e emite evento.

Fluxos utilizam `job_id` compartilhado para correlação em logs e dashboards.


## 8. Mapa de Dependências

| Componente | Depende de | Risco/Observação |
| --- | --- | --- |
| Agentes Celery | Redis (broker/resultado) | Dimensionar Redis para filas separadas por agente |
| DJENCollector | Conectividade DJEN, limites 60 req/min | Necessário backoff exponencial e cache de 24h |
| LLM Gemini | Google AI SDK, quota | Configurar pooling e observabilidade; fallback GPT-4 |
| Persistência Django | Banco (SQLite dev, PostgreSQL prod) | Garantir migrações antes dos jobs |
| ContextManager | Configurações de tokens | Validar limites por agente em ambiente de teste |
| Dashboards | Eventos pub/sub | Precisam de consumer assinado para receber updates |


## 9. Definition of Done (Sprint 2)

- [ ] Documento de especificação validado com Product Owner e equipe técnica.
- [ ] Contratos de payload/API revisados pelo time de backend.
- [ ] Fluxos aprovados pelo time de UX/Produto (alinhamento com storyboards).
- [ ] Dependências registradas no board de risco (Redis, DJEN, LLM quotas).
- [ ] Checklist replicado na issue #16 antes do encerramento.


## 10. Referências Cruzadas

- Canvas estratégico: `documentacao/canvas/canvas_jurisprudencia_agentes_ia.md`
- Storyboards de uso: `documentacao/storyboards_agentes.md`
- Modelos de dados Django: `backend/jurisprudencia/models.py`
- Planejamento de sprint: `documentacao/sprint_backlog_23_09.md`

