# 🗃️ Documentação dos Modelos Django - Sistema de Jurisprudência IA

Este documento detalha os modelos de dados implementados para o sistema de análise de jurisprudência com agentes de IA.

---

## 🎯 **Visão Geral**

Os modelos foram projetados para atender aos 4 cenários principais dos storyboards:
1. **Busca de Jurisprudência Favorável à Tese** (MVP)
2. **Análise Neutra da Jurisprudência**
3. **Estudo de Padrões por Vara/Tribunal**
4. **Análise Estratégica Antecipatória**

---

## 📊 **Diagrama de Relacionamentos**

```
BaseModel (abstract)
├── Julgado
├── AnaliseJurisprudenciaTese ──┐
├── JulgadoFavoravel ──────────┘
├── AnaliseJurisprudenciaNeutra
├── PadroesVaraTribunal
└── EstrategiaAntecipatoria
```

---

## 🏗️ **Modelos Implementados**

### **1. BaseModel (Abstract)**
**Propósito:** Modelo base com campos comuns de auditoria.

**Campos principais:**
- `id`: UUID como chave primária
- `criado_em`: Timestamp de criação
- `atualizado_em`: Timestamp de atualização
- `criado_por`: Referência ao usuário criador

**Padrão:** Todos os modelos herdam deste modelo base.

---

### **2. Julgado**
**Propósito:** Armazenar julgados coletados do DJEN.

**Campos principais:**
- `numero_processo`: Número do processo
- `titulo`: Título/Ementa do julgado
- `conteudo`: Conteúdo completo
- `data_publicacao`: Data de publicação
- `tribunal`, `vara`, `comarca`: Informações do órgão julgador
- `relator`: Relator responsável
- `djen_id`: ID único no DJEN
- `processado`: Flag de processamento pelos agentes
- `hash_conteudo`: Hash para controle de duplicatas

**Índices otimizados:**
- `tribunal + data_publicacao`
- `numero_processo`
- `djen_id`
- `hash_conteudo`

---

### **3. AnaliseJurisprudenciaTese**
**Propósito:** Análise de jurisprudência favorável a uma tese específica (Cenário 1).

**Campos principais:**
- `tese_juridica`: Tese analisada
- `termos_busca`: Lista de termos utilizados
- `filtros_aplicados`: Filtros da busca (JSON)
- `periodo_analise_inicio/fim`: Período analisado
- `total_julgados_encontrados/favoraveis`: Quantitativos
- `percentual_favorabilidade`: Score geral (0-100%)
- `argumentos_favoraveis`: Lista de argumentos principais
- `precedentes_fortes`: Precedentes de tribunais superiores
- `status`: processando, concluida, erro

**Relacionamentos:**
- `julgados_favoraveis`: Many-to-Many através de JulgadoFavoravel

---

### **4. JulgadoFavoravel**
**Propósito:** Tabela intermediária com score detalhado de favorabilidade.

**Campos principais:**
- `analise`: FK para AnaliseJurisprudenciaTese
- `julgado`: FK para Julgado
- `score_favorabilidade`: Score específico (0-100)
- `justificativa`: Explicação do score
- `eh_precedente_forte`: Flag para precedentes importantes
- `argumentos_chave`: Lista de argumentos identificados

**Índices:**
- `score_favorabilidade`
- `eh_precedente_forte`

---

### **5. AnaliseJurisprudenciaNeutra**
**Propósito:** Análise neutra da jurisprudência sobre um tema (Cenário 2).

**Campos principais:**
- `tema_juridico`: Tema analisado
- `filtros_aplicados`: Filtros aplicados (JSON)
- `periodo_analise_inicio/fim`: Período
- `total_julgados_analisados`: Total analisado
- `julgados_favoraveis/contrarios/neutros`: Distribuição
- `tendencia_majoritaria`: favoravel, contraria, dividida, neutra
- `argumentos_pro/contra`: Listas de argumentos
- `evolucao_temporal`: Evolução no tempo (JSON)

**Relacionamentos:**
- `julgados_representativos`: Many-to-Many com Julgado

---

### **6. PadroesVaraTribunal**
**Propósito:** Análise de padrões de julgamento por órgão (Cenário 3).

**Campos principais:**
- `tribunal`: Nome do tribunal
- `vara`: Vara específica (opcional)
- `tema_juridico`: Tema analisado
- `periodo_analise_inicio/fim`: Período
- `total_julgados_analisados`: Quantidade
- `padroes_julgamento`: Padrões identificados (JSON)
- `perfil_julgador`: Perfil do órgão (JSON)
- `precedentes_citados`: Precedentes mais citados
- `valores_indenizacao`: Estatísticas de valores (JSON)
- `teses_aceitas/rejeitadas`: Listas de teses
- `comparacao_outros_orgaos`: Comparações (JSON)

**Relacionamentos:**
- `julgados_analisados`: Many-to-Many com Julgado

**Constraint único:**
- `tribunal + vara + tema_juridico + periodo_analise_inicio + periodo_analise_fim`

---

### **7. EstrategiaAntecipatoria**
**Propósito:** Análise estratégica para casos específicos (Cenário 4).

**Campos principais:**
- `numero_processo`: Processo analisado
- `tribunal_destino`: Tribunal de destino
- `vara_destino`: Vara específica (opcional)
- `documentos_caso`: Lista de documentos (JSON)
- `resumo_caso`: Resumo do caso
- `probabilidade_sucesso`: Probabilidade calculada (%)
- `riscos_identificados`: Lista de riscos (JSON)
- `estrategias_mitigacao`: Estratégias (JSON)
- `argumentos_direcionados`: Argumentos específicos (JSON)
- `precedentes_recomendados`: Precedentes para citar (JSON)
- `pontos_atencao`: Pontos importantes (JSON)
- `cronograma_recomendado`: Timeline (JSON)

**Relacionamentos:**
- `padrao_vara_relacionado`: FK para PadroesVaraTribunal

**Validação (Machine Learning):**
- `resultado_real`: favoravel, desfavoravel, parcial, pendente
- `data_resultado`: Data do resultado real
- `observacoes_resultado`: Observações

---

## 🚀 **Funcionalidades Implementadas**

### **Auditoria Completa**
- Todos os registros têm UUID, timestamps e usuário criador
- Rastreabilidade total das operações

### **Índices Otimizados**
- Consultas por tribunal, data, status otimizadas
- Busca por scores e probabilidades eficiente
- Chaves únicas para evitar duplicatas

### **Flexibilidade JSON**
- Campos JSON para dados estruturados variáveis
- Permite evolução dos agentes sem mudança de schema
- Armazenamento eficiente de listas e objetos complexos

### **Relacionamentos Inteligentes**
- Many-to-Many com tabelas intermediárias detalhadas
- Foreign Keys com CASCADE/SET_NULL apropriados
- Relacionamentos que suportam os 4 cenários

---

## 📈 **Escalabilidade e Performance**

### **Índices Estratégicos**
```sql
-- Principais índices criados
CREATE INDEX ON julgado (tribunal, data_publicacao);
CREATE INDEX ON julgado (hash_conteudo);
CREATE INDEX ON analisejurisprudenciatese (status, criado_em);
CREATE INDEX ON julgadofavoravel (score_favorabilidade);
CREATE INDEX ON estrategiaantecipatoria (probabilidade_sucesso);
```

### **Constraints de Integridade**
- Unique constraints para evitar duplicatas
- Foreign keys para integridade referencial
- Campos obrigatórios bem definidos

---

## 🧪 **Validação dos Modelos**

### **Testes Implementados**
✅ Criação de migrações bem-sucedida
✅ Aplicação de migrações sem erros
✅ Todos os índices criados corretamente
✅ Relacionamentos funcionando
✅ Campos JSON operacionais

### **Próximos Passos**
- Testes unitários para cada modelo
- Validações de negócio
- Métodos personalizados nos modelos
- Admin interface para os modelos

---

## 🔗 **Vinculação com os Storyboards**

| Cenário | Modelo Principal | Modelos Relacionados |
|---------|------------------|---------------------|
| **1. Busca Favorável** | AnaliseJurisprudenciaTese | Julgado, JulgadoFavoravel |
| **2. Análise Neutra** | AnaliseJurisprudenciaNeutra | Julgado |
| **3. Padrões de Vara** | PadroesVaraTribunal | Julgado |
| **4. Estratégia Antecipatória** | EstrategiaAntecipatoria | PadroesVaraTribunal |

---

**Status:** ✅ **CONCLUÍDO**
**Issue:** #3 - Modelos de Dados - Estrutura de Armazenamento
**Branch:** `feature/models-django-jurisprudencia`
