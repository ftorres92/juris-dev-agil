# 🤖 Guia de Automação GitHub - Juris-Dev-Agil

> **Autor**: Fernando Torres  
> **Data**: 26/09/2024  
> **Versão**: 1.0  

## 📋 Visão Geral

Este documento explica os scripts e workflows de automação implementados para melhorar a integração com GitHub no projeto Juris-Dev-Agil.

## 🚀 Scripts Implementados

### 1. **Script Principal de Automação** (`scripts/github-automation.sh`)

**O que faz:**
- Atualiza status das issues da Sprint 3
- Cria milestone para Sprint 4
- Atribui issues à Sprint 4 com labels apropriados
- Cria template de Pull Request
- Gera relatório de progresso automático

**Como usar:**
```bash
# Executar automação completa
./scripts/github-automation.sh

# Verificar se está funcionando
chmod +x scripts/github-automation.sh
```

**Funcionalidades:**
- ✅ Verificação de autenticação GitHub CLI
- ✅ Atualização automática de status de issues
- ✅ Criação de milestones
- ✅ Atribuição de labels e prioridades
- ✅ Geração de relatórios de progresso
- ✅ Criação de templates padronizados

### 2. **Gerador de Relatórios** (`scripts/generate_progress_report.py`)

**O que faz:**
- Analisa progresso das sprints automaticamente
- Gera relatórios em Markdown com métricas
- Calcula percentuais de conclusão
- Identifica próximas prioridades

**Como usar:**
```bash
# Gerar relatório manual
python scripts/generate_progress_report.py

# Ou executar via script principal
./scripts/github-automation.sh
```

**Saída:**
- Relatório em `documentacao/progress_report_auto.md`
- Métricas de progresso das sprints
- Análise de prioridades
- Recomendações de próximas ações

## 🔧 Workflows GitHub Actions

### 1. **CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)

**O que faz:**
- Executa testes automaticamente em PRs
- Valida código com linting (flake8, black, isort)
- Testa em múltiplas versões do Python (3.11, 3.12)
- Faz deploy automático para produção

**Triggers:**
- Push para branches `main`, `develop`, `sprint3/*`
- Pull requests para `main` e `develop`

**Benefícios:**
- ✅ Qualidade de código garantida
- ✅ Testes automatizados
- ✅ Deploy seguro
- ✅ Feedback rápido para desenvolvedores

### 2. **Automação de Documentação** (`.github/workflows/documentation.yml`)

**O que faz:**
- Gera documentação da API automaticamente
- Atualiza relatórios de progresso
- Commit automático de mudanças na documentação

**Triggers:**
- Mudanças em `documentacao/**`
- Mudanças em `backend/**`

**Benefícios:**
- ✅ Documentação sempre atualizada
- ✅ Relatórios automáticos
- ✅ Sincronização de docs com código

## 📊 Templates e Padrões

### 1. **Template de Pull Request** (`.github/pull_request_template/pull_request_template.md`)

**Estrutura:**
- Descrição das mudanças
- Link para issue relacionada
- Checklist de qualidade
- Instruções de teste
- Screenshots (quando aplicável)

### 2. **Labels Padronizados**

**Sprints:**
- `sprint/sprint-3` - Sprint 3 (Verde)
- `sprint/sprint-4` - Sprint 4 (Amarelo)

**Prioridades:**
- `priority/must-have` - Must Have (Vermelho)
- `priority/should-have` - Should Have (Laranja)
- `priority/could-have` - Could Have (Azul)

## 🎯 Como Usar no Dia a Dia

### **Para Desenvolvedores:**

1. **Antes de começar uma tarefa:**
   ```bash
   # Verificar issues atribuídas
   gh issue list --assignee @me --state open
   
   # Ver progresso da sprint
   python scripts/generate_progress_report.py
   ```

2. **Durante o desenvolvimento:**
   ```bash
   # Criar branch para nova feature
   git checkout -b feature/nova-funcionalidade
   
   # Fazer commits com mensagens claras
   git commit -m "feat: implementa nova funcionalidade"
   ```

3. **Ao finalizar uma tarefa:**
   ```bash
   # Criar Pull Request
   gh pr create --title "feat: implementa nova funcionalidade" --body "Closes #XX"
   
   # Executar automação
   ./scripts/github-automation.sh
   ```

### **Para Scrum Master/Product Owner:**

1. **Daily Scrum:**
   ```bash
   # Verificar progresso geral
   python scripts/generate_progress_report.py
   
   # Ver issues em andamento
   gh issue list --state open --label "sprint/sprint-4"
   ```

2. **Sprint Planning:**
   ```bash
   # Ver backlog organizado
   gh project view 8 --owner ftorres92
   
   # Atribuir issues
   gh issue edit XX --add-assignee @usuario
   ```

3. **Sprint Review:**
   ```bash
   # Gerar relatório final
   ./scripts/github-automation.sh
   
   # Ver métricas de conclusão
   gh issue list --state closed --label "sprint/sprint-4"
   ```

## 📈 Métricas e Relatórios

### **Relatórios Automáticos:**

1. **Progress Report** (`documentacao/progress_report_auto.md`)
   - Progresso das sprints
   - Métricas de issues
   - Próximas prioridades
   - Análise de qualidade

2. **GitHub Projects** (Projeto ID: 8)
   - Organização visual das issues
   - Controle de progresso
   - Rastreabilidade completa

### **Comandos Úteis:**

```bash
# Ver todas as issues
gh issue list --state all

# Ver issues por sprint
gh issue list --label "sprint/sprint-4"

# Ver PRs pendentes
gh pr list --state open

# Ver progresso do projeto
gh project view 8 --owner ftorres92
```

## 🔧 Configuração Inicial

### **Pré-requisitos:**
1. GitHub CLI instalado (`brew install gh`)
2. Autenticação configurada (`gh auth login`)
3. Permissões de escrita no repositório

### **Primeira Execução:**
```bash
# Tornar scripts executáveis
chmod +x scripts/github-automation.sh
chmod +x scripts/generate_progress_report.py

# Executar automação inicial
./scripts/github-automation.sh

# Verificar se funcionou
gh issue list --state open --label "sprint/sprint-4"
```

## 🚨 Troubleshooting

### **Problemas Comuns:**

1. **Erro de autenticação:**
   ```bash
   gh auth login
   ```

2. **Script não executa:**
   ```bash
   chmod +x scripts/github-automation.sh
   ```

3. **Erro de permissão:**
   - Verificar se tem acesso de escrita ao repositório
   - Verificar se está na branch correta

4. **Issues não aparecem:**
   ```bash
   # Verificar se está no repositório correto
   gh repo view
   
   # Verificar issues
   gh issue list --state all
   ```

## 📚 Recursos Adicionais

### **Documentação GitHub CLI:**
- [GitHub CLI Documentation](https://cli.github.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)

### **Comandos Avançados:**
```bash
# Ver detalhes de uma issue
gh issue view XX

# Editar issue
gh issue edit XX --add-label "priority/must-have"

# Criar issue
gh issue create --title "Nova Issue" --body "Descrição" --label "sprint/sprint-4"

# Ver logs do workflow
gh run list
gh run view XX
```

## 🎉 Benefícios Alcançados

### **Produtividade:**
- ✅ Automação de tarefas repetitivas
- ✅ Relatórios automáticos
- ✅ Qualidade de código garantida
- ✅ Deploy automatizado

### **Organização:**
- ✅ Issues bem estruturadas
- ✅ Labels padronizados
- ✅ Milestones organizados
- ✅ Rastreabilidade completa

### **Qualidade:**
- ✅ Testes automatizados
- ✅ Linting obrigatório
- ✅ Documentação atualizada
- ✅ Feedback rápido

---

**🎯 Resultado:** O projeto agora tem uma integração robusta e automatizada com GitHub, proporcionando melhor visibilidade, qualidade e produtividade para toda a equipe!
