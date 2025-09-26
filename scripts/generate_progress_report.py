#!/usr/bin/env python3
"""
Script para gerar relatórios de progresso automáticos
Autor: Fernando Torres
Data: 26/09/2024
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_gh_command(command):
    """Executa comando gh CLI e retorna resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
        return None

def get_issues_data():
    """Obtém dados das issues do GitHub"""
    command = "gh issue list --state all --json number,title,state,labels,createdAt,updatedAt"
    result = run_gh_command(command)
    
    if result:
        return json.loads(result)
    return []

def get_pr_data():
    """Obtém dados dos PRs do GitHub"""
    command = "gh pr list --state all --json number,title,state,createdAt,updatedAt"
    result = run_gh_command(command)
    
    if result:
        return json.loads(result)
    return []

def analyze_sprint_progress(issues):
    """Analisa progresso das sprints"""
    sprint3_issues = [i for i in issues if any('sprint/sprint-3' in label.get('name', '') for label in i.get('labels', []))]
    sprint4_issues = [i for i in issues if any('sprint/sprint-4' in label.get('name', '') for label in i.get('labels', []))]
    
    sprint3_completed = len([i for i in sprint3_issues if i['state'] == 'CLOSED'])
    sprint3_total = len(sprint3_issues)
    sprint3_progress = (sprint3_completed / sprint3_total * 100) if sprint3_total > 0 else 0
    
    sprint4_completed = len([i for i in sprint4_issues if i['state'] == 'CLOSED'])
    sprint4_total = len(sprint4_issues)
    sprint4_progress = (sprint4_completed / sprint4_total * 100) if sprint4_total > 0 else 0
    
    return {
        'sprint3': {
            'completed': sprint3_completed,
            'total': sprint3_total,
            'progress': sprint3_progress
        },
        'sprint4': {
            'completed': sprint4_completed,
            'total': sprint4_total,
            'progress': sprint4_progress
        }
    }

def generate_markdown_report(issues, prs, sprint_data):
    """Gera relatório em Markdown"""
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    # Estatísticas gerais
    total_issues = len(issues)
    open_issues = len([i for i in issues if i['state'] == 'OPEN'])
    closed_issues = len([i for i in issues if i['state'] == 'CLOSED'])
    
    total_prs = len(prs)
    open_prs = len([i for i in prs if i['state'] == 'OPEN'])
    merged_prs = len([i for i in prs if i['state'] == 'MERGED'])
    
    # Issues por prioridade
    high_priority = len([i for i in issues if any('priority/must-have' in label.get('name', '') for label in i.get('labels', []))])
    medium_priority = len([i for i in issues if any('priority/should-have' in label.get('name', '') for label in i.get('labels', []))])
    low_priority = len([i for i in issues if any('priority/could-have' in label.get('name', '') for label in i.get('labels', []))])
    
    report = f"""# 📊 Relatório de Progresso - {current_date}

## 🎯 Resumo Executivo

### 📈 Métricas Gerais
- **Total de Issues**: {total_issues}
- **Issues Abertas**: {open_issues}
- **Issues Fechadas**: {closed_issues}
- **Total de PRs**: {total_prs}
- **PRs Abertos**: {open_prs}
- **PRs Mergeados**: {merged_prs}

## 🏃‍♂️ Progresso das Sprints

### ✅ Sprint 3 - Integração e Validação
- **Progresso**: {sprint_data['sprint3']['progress']:.1f}%
- **Concluídas**: {sprint_data['sprint3']['completed']}/{sprint_data['sprint3']['total']}
- **Status**: {'✅ CONCLUÍDA' if sprint_data['sprint3']['progress'] >= 100 else '🔄 EM ANDAMENTO'}

### 🚀 Sprint 4 - Agentes e Interface
- **Progresso**: {sprint_data['sprint4']['progress']:.1f}%
- **Concluídas**: {sprint_data['sprint4']['completed']}/{sprint_data['sprint4']['total']}
- **Status**: {'✅ CONCLUÍDA' if sprint_data['sprint4']['progress'] >= 100 else '🔄 EM ANDAMENTO'}

## 🔥 Priorização Atual

### Alta Prioridade (Must Have)
- **Total**: {high_priority} issues
- **Status**: {'✅ Todas concluídas' if high_priority == 0 else '🔄 Em andamento'}

### Média Prioridade (Should Have)
- **Total**: {medium_priority} issues
- **Status**: {'✅ Todas concluídas' if medium_priority == 0 else '🔄 Em andamento'}

### Baixa Prioridade (Could Have)
- **Total**: {low_priority} issues
- **Status**: {'✅ Todas concluídas' if low_priority == 0 else '🔄 Em andamento'}

## 📋 Próximas Ações Recomendadas

### 🎯 Para Hoje (26/09)
1. **Finalizar Sprint 3**: Completar issues pendentes
2. **Iniciar Sprint 4**: Começar com D0 (Página Inicial)
3. **Atualizar Documentação**: Manter docs sincronizadas

### 📅 Para Esta Semana
1. **D0** - Página Inicial do Sistema (6 SP) 🔥
2. **A1** - AgenteClassificadorTese (8 SP) 🔥
3. **D2** - Dashboard Django com Métricas (8 SP) 🔥

## 🧪 Qualidade e Testes

### ✅ Critérios de Qualidade
- [ ] Todas as issues da Sprint 3 testadas
- [ ] Interface responsiva validada
- [ ] Performance otimizada
- [ ] Documentação atualizada
- [ ] Testes automatizados funcionando

## 📊 Métricas de Sucesso

### 🎯 Sprint 3
- **Objetivo**: Integração DJEN + Interface Django
- **Status**: {'✅ ALCANÇADO' if sprint_data['sprint3']['progress'] >= 100 else '🔄 EM PROGRESSO'}

### 🎯 Sprint 4
- **Objetivo**: Agentes de IA + Interface Avançada
- **Status**: {'✅ ALCANÇADO' if sprint_data['sprint4']['progress'] >= 100 else '🔄 EM PROGRESSO'}

---
*Relatório gerado automaticamente em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}*
*Gerado pelo sistema de automação GitHub*
"""

    return report

def main():
    """Função principal"""
    print("🚀 Gerando relatório de progresso...")
    
    # Obter dados
    issues = get_issues_data()
    prs = get_pr_data()
    
    if not issues:
        print("❌ Erro: Não foi possível obter dados das issues")
        sys.exit(1)
    
    # Analisar progresso
    sprint_data = analyze_sprint_progress(issues)
    
    # Gerar relatório
    report = generate_markdown_report(issues, prs, sprint_data)
    
    # Salvar arquivo
    output_file = Path("documentacao/progress_report_auto.md")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Relatório gerado: {output_file}")
    print(f"📊 Sprint 3: {sprint_data['sprint3']['progress']:.1f}%")
    print(f"📊 Sprint 4: {sprint_data['sprint4']['progress']:.1f}%")

if __name__ == "__main__":
    main()
