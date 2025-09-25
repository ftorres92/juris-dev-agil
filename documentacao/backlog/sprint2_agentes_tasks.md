# 📌 Sprint 2 - Backlog de Implementação dos Agentes

> **Referência**: [Especificação Técnica Sprint 2](../architecture/agentes_sprint2.md)
> **História de Usuário**: [#16 - Definição de Agentes - Especificações](https://github.com/ftorres92/Juris-Dev-agil/issues/16)

Este backlog detalha as tarefas necessárias para implementar os agentes e componentes definidos na Sprint 2. Cada item deve ser criado como uma issue no GitHub com o label `sprint/sprint-2`, vinculada à issue #16.

**⚠️ IMPORTANTE**: As tarefas de implementação dos agentes (T3-T9) dependem da conclusão da Sprint 3 (integração frontend/backend e validação DJEN).

## ✅ Tarefas Prioritárias

| Item | Descrição | Entregáveis | Dependências |
| --- | --- | --- | --- |
| T1 | Configurar infraestrutura Celery para filas dedicadas dos agentes | Filas `juris.classificador`, `juris.neutro`, `juris.vara`, `juris.estrategico`; workers configurados; documentação de execução | Redis operante, settings Django |
| T2 | Implementar `DJENCollector` com cache Redis e rate limiting | Classe Python com métodos `search`/`fetch_by_ids`, cache 24h, backoff exponencial, testes básicos | Redis, especificação DJEN |
| T3 | Implementar pipeline do `AgenteClassificadorTese` | Tarefa Celery, prompts Gemini/GPT-4, persistência em `AnaliseJurisprudenciaTese` e `JulgadoFavoravel`, eventos `juris.analise_tese.ready` | T1, T2, modelos Django |
| T4 | Implementar pipeline do `AgenteAnalisadorNeutro` | Tarefa Celery, clusterização básica, atualização `AnaliseJurisprudenciaNeutra`, evento `analisador_neutro.completed` | T1, T2 |
| T5 | Implementar pipeline do `AgenteAnalisadorVara` | Tarefa Celery, estatísticas comparativas, atualização `PadroesVaraTribunal`, evento `padrao_vara.updated` | T1, T2 |
| T6 | Implementar pipeline do `AgenteEstrategicoAntecipatorio` | Tarefa Celery, integração com `PadroesVaraTribunal`, cálculo probabilidade, evento `estrategia.completed` | T1, T5 |
| T7 | Configurar observabilidade e logging estruturado dos agentes | Logger `juris.agentes`, métricas Prometheus (latência, tokens, erros), rastreamento `job_id` | T1 |
| T8 | Expor endpoints REST para acionar análises e consultar status | Rotas conforme seção 6.1, serializers/validators, integração com Celery | T1, modelos, pipelines |
| T9 | Documentar prompts e política de fallback LLM | Registro em `docs/llm_prompts.md`, procedimentos de fallback, checklist de revisão | T3-T6 |

## 🎨 Melhorias Interface Django (Sprint 3+)

| Item | Descrição | Entregáveis | Dependências |
| --- | --- | --- | --- |
| D1 | Aprimorar templates Django com Bootstrap 5 | Templates responsivos, componentes reutilizáveis, design moderno | T8 |
| D2 | Implementar Dashboard Django com métricas | Dashboard responsivo, cards de estatísticas, gráficos Chart.js | D1, T8 |
| D3 | Melhorar interface de consulta de jurisprudência | Formulário aprimorado, filtros avançados, validação client-side | D1, T8 |
| D4 | Desenvolver visualização de resultados aprimorada | Lista de julgados, filtros por favorabilidade, paginação | D1, T8 |
| D5 | Implementar gráficos e estatísticas | Charts interativos, métricas de favorabilidade, comparações | D1, biblioteca Chart.js |
| D6 | Configurar Django REST Framework | API endpoints, serializers, autenticação JWT | T8 |
| D7 | Implementar exportação de relatórios | Download PDF/DOCX, templates de relatório, preview | D1, T8 |
| D8 | Configurar Django Channels para WebSocket | Atualizações em tempo real, notificações de status | D6 |
| D9 | Implementar testes e CI/CD | Testes Django, testes de integração, deploy automatizado | D1-D8 |

## 🔁 Tarefas de Suporte

| Item | Descrição | Entregáveis |
| --- | --- | --- |
| S1 | Preparar dataset rotulado mínimo para validação das métricas | Dataset anonimizado, script de avaliação | 
| S2 | Definir testes automáticos (unitários e integração) para pipelines | Testes Django + factories + mocks LLM/DJEN | 
| S3 | Atualizar dashboards/consumidores para eventos dos agentes | Consumers inscritos, atualização visual inicial |
| S4 | Melhorar templates Django com componentes reutilizáveis | Base templates, includes, partials | 
| S5 | Configurar Chart.js para visualização de dados | Gráficos responsivos, métricas dos agentes | 

## ✅ Critérios de Conclusão

- Todos os itens T1–T9 criados e priorizados no GitHub Projects.
- Itens de suporte S1–S5 avaliados pelo time (pelo menos um responsável designado).
- Melhorias Django D1–D9 planejadas para Sprint 3.
- Issue #16 atualizada com checklist e links das issues derivadas.
- Documentação alinhada com as implementações planejadas.

## 📆 Atualizações Recentes

- 2025-09-25 · Sprint 2 · Issues #16 e #24: Página Django `GET /djen/consulta/` disponibilizada para consultas por termo (layout Bootstrap inspirado nas telas de intimações).
- 2025-09-25 · Sprint 2 · Issues #16 e #24: Fluxo REST descontinuado; validação do DJEN passa a ocorrer exclusivamente via interface server-side.
- 2025-09-25 · Sprint 3 · Decisão: Frontend React removido do escopo; foco em melhorias Django com Bootstrap 5 e Chart.js.
- 2025-09-25 · Sprint 3 · Planejamento: 9 tarefas Django (D1-D9) adicionadas para aprimorar interface existente.
