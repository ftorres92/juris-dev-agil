# 🤖 Agentes para Análise de Jurisprudência Estratégica

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://djangoproject.com)


## 👥 **Equipe**

| Nome | GitHub | Papel |
|------|--------|-------|
| Fernando Torres | [@ftorres92](https://github.com/ftorres92) | 🛠️ Líder Técnico |
| Fernando Lobo | [@fernandolobo](https://github.com/fernandoleme01)| 🎯 Scrum Master |
| Marcio Ferreira | [@MarcioFerrer](https://github.com/MarcioFerrer) | 📋 Product Owner |
| Elinton Camacho Piratello | [@elintonpiratello] | 🔬 Pesquisador Científico |
| Flavio Eustaquio de Oliveira | [@flavioeustaquio]| 🚀 Dev de Protótipos |
| Heloiza de Oliveira Souza | [@heloizaoliveira] | 🚀 Dev de Protótipos |
| José Ramos Damasceno Filho | [@joseramos] | 🚀 Dev de Protótipos |

## 🎯 **Visão Geral da Solução**

Sistema inovador de **agentes de IA especializados** que resolve o problema crítico da **pesquisa de jurisprudência mista** no mercado jurídico brasileiro. Através de 4 cenários estratégicos únicos, o sistema classifica automaticamente julgados como favoráveis ou desfavoráveis à tese do cliente, oferecendo insights preditivos e estratégias personalizadas por órgão julgador.

**Diferencial**: Único sistema no mercado que elimina julgados desfavoráveis da pesquisa, economizando 80% do tempo de análise jurídica e aumentando significativamente as chances de sucesso nos processos.

## 🎯 **Problema Resolvido**

Atualmente, quando fazemos pesquisa de jurisprudência por **termos**, o sistema retorna **julgados mistos** - alguns favoráveis e outros **desfavoráveis à nossa tese**. Isso gera:

- ⏰ **Perda de tempo**: Advogados precisam ler manualmente cada julgado
- ❌ **Resultados mistos**: Pesquisa por termo não filtra por posicionamento  
- 🤔 **Dúvidas estratégicas**: Não sabemos se a jurisprudência é favorável
- 📊 **Falta de insights**: Não entendemos padrões de julgamento específicos

## 🚀 **Solução: 4 Cenários Estratégicos**

### 1. 🔍 **Busca de Jurisprudência Favorável à Nossa Tese**
- **Objetivo**: Encontrar julgados que **corroborem nossa tese**
- **Processo**: Pesquisa por termo + Agente classifica se é favorável/desfavorável
- **Resultado**: Lista filtrada apenas com julgados favoráveis

### 2. 📊 **Análise da Jurisprudência Real (Sem Viés)**
- **Objetivo**: Entender a **jurisprudência real** sobre o tema
- **Processo**: Busca ampla + Agente analisa tendência geral
- **Resultado**: Entendimento majoritário sem forçar nossa tese

### 3. 🏛️ **Estudo de Padrões por Vara/Tribunal**
- **Objetivo**: Analisar como **órgãos específicos** julgam determinado tema
- **Processo**: Busca por vara/tribunal + Análise de padrões
- **Resultado**: "Sobre o tema X, essa vara decide da seguinte forma..."

### 4. 🎯 **Análise Estratégica Antecipatória**
- **Objetivo**: Antecipar como uma vara específica julgará nosso caso
- **Processo**: Análise histórica da vara + Predição baseada em padrões
- **Resultado**: Estratégia personalizada para cada órgão julgador

## 🏗️ **Arquitetura Técnica**

### **Sistema de Agentes Especializados**
```
ia/agentes/
├── classificador_tese.py          # Agente Classificador por Tese
├── analisador_neutro.py          # Agente Analisador Neutro  
├── analisador_vara.py            # Agente Analisador por Vara
├── estrategico_antecipatorio.py   # Agente Estratégico Antecipatório
└── base_agent.py                 # Classe base para agentes

ia/pipelines/
├── djen_processor.py             # Pipeline de processamento DJEN
└── agent_coordinator.py         # Coordenador entre agentes

ia/models/
├── analise_jurisprudencia_tese.py      # AnaliseJurisprudenciaTese
├── analise_jurisprudencia_neutra.py   # AnaliseJurisprudenciaNeutra
├── padroes_vara_tribunal.py            # PadroesVaraTribunal
└── estrategia_antecipatoria.py        # EstrategiaAntecipatoria
```

### **Pipeline de Processamento**
```
DJEN → Agentes Especializados → Análises Estratégicas → Dashboard → Usuário
```

## 📁 **Estrutura do Projeto**

```
juris-dev-agil/
├── documentacao/          # Documentação completa do projeto
│   ├── canvas/           # Canvas do projeto
│   └── backlog/          # Backlog e PBB
├── ia/                   # Sistema de Agentes de IA
│   ├── agentes/          # Agentes especializados
│   ├── pipelines/        # Pipeline de processamento
│   └── models/           # Modelos de dados
├── backend/              # Aplicação backend Django
├── frontend/             # Aplicação web React
├── app/                  # Aplicativo mobile React Native
└── README.md             # Este arquivo
```

## 📚 **Documentação Completa**

### 📋 **Canvas do Projeto**
- [Canvas de Análise de Jurisprudência](documentacao/canvas/canvas_jurisprudencia_agentes_ia.md)
- Definição completa do projeto com dados, skills, stakeholders e métricas

### 📊 **Backlog Detalhado**
- [Backlog CSV](documentacao/backlog/backlog_jurisprudencia_agentes_ia_final.csv)
- 16 issues organizadas em 6 sprints (Sprint 1-6) com metodologia MoSCoW
- Estimativas e dependências técnicas
- [PBB Completo](documentacao/backlog/PBB_PROBLEMA_PERSONAS_EXPECTATIVAS_FEATURES.md)

### 🎯 **GitHub Project**
- [GitHub Issues](https://github.com/ftorres92/juris-dev-agil/issues) - 16 issues organizadas
- [GitHub Project](https://github.com/ftorres92/juris-dev-agil/projects) - Board de acompanhamento
- [Guia para Times](documentacao/backlog/GUIA_PARA_OS_TIMES.md) - Instruções para desenvolvimento

## 🛠️ **Configuração do Ambiente**

### **Pré-requisitos**
- Python 3.13+
- Django 4.x
- PostgreSQL
- Redis
- pip

### **Instalação**

1. **Clone o repositório:**
```bash
git clone https://github.com/ftorres92/juris-dev-agil.git
cd juris-dev-agil
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual:**
```bash
# No macOS/Linux:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

4. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

5. **Configure o banco de dados:**
```bash
python manage.py migrate
```

6. **Execute o servidor:**
```bash
python manage.py runserver
```

## 📈 **Métricas de Sucesso**

### **Métricas Técnicas**
- **Precisão de classificação**: > 90% na identificação favorável/desfavorável
- **Tempo de processamento**: < 3 minutos para cada análise
- **Disponibilidade**: > 99.5% para todos os agentes
- **Cache hit ratio**: > 80% entre consultas similares

### **Métricas de Negócio**
- **Adoção**: > 80% dos usuários ativos
- **Engagement**: > 10 consultas por usuário/mês
- **Satisfação**: > 4.7/5 estrelas
- **Revenue impact**: +25% em planos premium

## 🎯 **Roadmap de Implementação**

### **Sprint 1-2: Setup e Planejamento**
- Configuração do ambiente de desenvolvimento
- Definição de arquitetura e especificações
- Planejamento detalhado dos agentes

### **Sprint 3: MVP - Busca Favorável à Tese**
- AgenteClassificadorTese para classificar julgados
- Interface básica para consulta de julgados favoráveis
- Algoritmo de classificação favorável/desfavorável
- Integração DJEN e modelos de dados

### **Sprint 4: Análise Neutra**
- AgenteAnalisadorNeutro para análise objetiva
- Dashboard para análise neutra
- Identificação de argumentos pró e contra

### **Sprint 5: Padrões por Vara**
- AgenteAnalisadorVara para padrões específicos
- Relatório: "Sobre o tema X, essa vara decide..."
- Geração de perfil do julgador

### **Sprint 6: Estratégia Antecipatória**
- AgenteEstrategicoAntecipatorio para predições
- Sistema de argumentos direcionados
- Relatórios exportáveis em PDF/DOCX

## 🤝 **Contribuição**

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request


## 📞 **Contato**

- **GitHub**: [@ftorres92](https://github.com/ftorres92)
- **Projeto**: [juris-dev-agil](https://github.com/ftorres92/juris-dev-agil)


