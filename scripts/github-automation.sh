#!/bin/bash

# GitHub Automation Script para Juris-Dev-Agil
# Autor: Fernando Torres
# Data: 26/09/2024

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Função para sucesso
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Função para erro
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para warning
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar se gh CLI está instalado
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI não está instalado. Instale com: brew install gh"
        exit 1
    fi
    success "GitHub CLI encontrado"
}

# Verificar autenticação
check_auth() {
    if ! gh auth status &> /dev/null; then
        error "Não autenticado no GitHub. Execute: gh auth login"
        exit 1
    fi
    success "Autenticado no GitHub"
}

# Atualizar status das issues da Sprint 3
update_sprint3_status() {
    log "Atualizando status das issues da Sprint 3..."
    
    # Issues concluídas da Sprint 3
    local completed_issues=("45" "56" "38")
    
    for issue in "${completed_issues[@]}"; do
        log "Fechando issue #$issue"
        gh issue close "$issue" --comment "✅ Sprint 3 concluída - Issue implementada e testada"
        success "Issue #$issue fechada"
    done
}

# Criar milestone para Sprint 4
create_sprint4_milestone() {
    log "Criando milestone para Sprint 4..."
    
    local milestone_date=$(date -d "+4 weeks" +%Y-%m-%d 2>/dev/null || date -v+4w +%Y-%m-%d)
    
    gh api repos/:owner/:repo/milestones \
        --method POST \
        --field title="Sprint 4 - Agentes e Interface" \
        --field description="Implementação dos agentes de IA e melhorias na interface Django" \
        --field due_on="$milestone_date" || warning "Milestone pode já existir"
    
    success "Milestone Sprint 4 criado"
}

# Atribuir issues à Sprint 4
assign_sprint4_issues() {
    log "Atribuindo issues à Sprint 4..."
    
    # Issues da Sprint 4
    local sprint4_issues=("50" "51" "52" "53" "54" "55" "57" "58" "46" "47" "48" "49")
    
    for issue in "${sprint4_issues[@]}"; do
        log "Atribuindo issue #$issue à Sprint 4"
        gh issue edit "$issue" --add-label "sprint/sprint-4" --add-label "priority/must-have"
        success "Issue #$issue atribuída à Sprint 4"
    done
}

# Criar template de PR
create_pr_template() {
    log "Criando template de Pull Request..."
    
    mkdir -p .github/pull_request_template
    
    cat > .github/pull_request_template/pull_request_template.md << 'EOF'
# 📋 Pull Request - Juris-Dev-Agil

## 🎯 Descrição
<!-- Descreva brevemente as mudanças implementadas -->

## 🔗 Issue Relacionada
<!-- Link para a issue: Closes #XX -->

## ✅ Checklist
- [ ] Código testado localmente
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Interface responsiva (se aplicável)
- [ ] Performance validada (se aplicável)

## 🧪 Como Testar
<!-- Instruções para testar as mudanças -->

## 📸 Screenshots (se aplicável)
<!-- Adicione screenshots da interface -->

## 📝 Notas Adicionais
<!-- Qualquer informação adicional relevante -->
EOF

    success "Template de PR criado"
}

# Gerar relatório de progresso
generate_progress_report() {
    log "Gerando relatório de progresso..."
    
    local report_file="documentacao/progress_report_$(date +%Y%m%d).md"
    
    cat > "$report_file" << EOF
# 📊 Relatório de Progresso - $(date +%d/%m/%Y)

## 🎯 Sprint 3 - Status
- **Issues Concluídas**: $(gh issue list --state closed --label "sprint/sprint-3" --json number | jq length)
- **Issues Pendentes**: $(gh issue list --state open --label "sprint/sprint-3" --json number | jq length)

## 🚀 Sprint 4 - Preparação
- **Issues Planejadas**: $(gh issue list --state open --label "sprint/sprint-4" --json number | jq length)
- **Milestone**: Sprint 4 - Agentes e Interface

## 📈 Métricas Gerais
- **Total de Issues**: $(gh issue list --state all --json number | jq length)
- **Issues Abertas**: $(gh issue list --state open --json number | jq length)
- **Issues Fechadas**: $(gh issue list --state closed --json number | jq length)

## 🔥 Próximas Prioridades
1. D0 - Página Inicial do Sistema
2. A1 - AgenteClassificadorTese
3. D2 - Dashboard Django com Métricas

---
*Relatório gerado automaticamente em $(date)*
EOF

    success "Relatório gerado: $report_file"
}

# Função principal
main() {
    log "🚀 Iniciando automação GitHub para Juris-Dev-Agil"
    
    check_gh_cli
    check_auth
    
    update_sprint3_status
    create_sprint4_milestone
    assign_sprint4_issues
    create_pr_template
    generate_progress_report
    
    success "🎉 Automação GitHub concluída com sucesso!"
}

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
