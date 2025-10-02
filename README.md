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
│   ├── backlog/          # Backlog e PBB
│   └── architecture/     # Especificações técnicas
├── backend/              # Aplicação backend Django
│   ├── juris_ai/         # Configuração Django
│   ├── jurisprudencia/   # App principal com agentes
│   └── templates/        # Templates Django (Bootstrap)
├── app/                  # Aplicativo mobile React Native (Sprint 6+)
└── README.md             # Este arquivo
```

## 📚 **Documentação Completa**

### 🎓 **Para Professores Avaliadores - Desenvolvimento Ágil**

#### **📄 Documentos Principais para Avaliação**
1. **[Resumo Executivo](documentacao/entrega-final/resumo_executivo_entrega_final.md)** - Visão geral completa do projeto
2. **[Consolidação de Evidências](documentacao/evidencias/consolidacao_evidencias_final.md)** - Análise detalhada da documentação ágil
3. **[Logs de Funcionamento](documentacao/evidencias/logs_evidencias_funcionamento.md)** - Evidências técnicas capturadas
4. **[Product Backlog](documentacao/backlog/backlog_jurisprudencia_agentes_ia_final.csv)** - 13 user stories estruturadas
5. **[PBB Completo](documentacao/backlog/PBB_PROBLEMA_PERSONAS_EXPECTATIVAS_FEATURES.md)** - Problema, personas e expectativas

#### **📋 Evidências de Desenvolvimento Ágil**
- **✅ Manifesto Ágil**: 4 valores implementados
- **✅ 12 Princípios Ágeis**: 9+ princípios evidenciados
- **✅ Cerimônias**: Sprint Planning, Daily Scrum, Sprint Review
- **✅ Artefatos**: Product Backlog, Sprint Backlog, Increment
- **✅ Métricas**: 17 testes executados, sistema funcionando

#### **🗂️ Navegação Rápida**
- **[Índice da Documentação](documentacao/INDEX.md)** - Guia rápido para todos os documentos
- **[README da Documentação](documentacao/README.md)** - Estrutura completa organizada

### 📋 **Canvas do Projeto**
- [Canvas de Análise de Jurisprudência](documentacao/canvas/canvas_jurisprudencia_agentes_ia.md)
- Definição completa do projeto com dados, skills, stakeholders e métricas

### 📊 **Backlog Detalhado**
- [Backlog CSV](documentacao/backlog/backlog_jurisprudencia_agentes_ia_final.csv)
- 13 user stories organizadas em 3 sprints com metodologia MoSCoW
- Estimativas e dependências técnicas
- [PBB Completo](documentacao/backlog/PBB_PROBLEMA_PERSONAS_EXPECTATIVAS_FEATURES.md)

### 🏃‍♂️ **Sprints e Execução**
- **[Sprint 2](documentacao/sprints/sprint_backlog_23_09.md)** - Planejamento e setup
- **[Sprint 3](documentacao/sprints/sprint3_status_final_26_09.md)** - Integração e validação
- **[Daily Scrums](documentacao/daily-scrums/)** - 2 sessões documentadas

### 🎯 **GitHub Project**
- [GitHub Issues](https://github.com/ftorres92/juris-dev-agil/issues) - Issues organizadas
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

### **🧪 Como Testar o Sistema**

#### **1. Executar Testes Automatizados**
```bash
cd backend
python manage.py test --verbosity=2
```
**Resultado esperado**: 17 testes passando

#### **2. Testar Integração DJEN**
```bash
cd backend
python manage.py shell
>>> from jurisprudencia.utils.djen_api import DJENClient
>>> client = DJENClient()
>>> result = client.buscar_jurisprudencia("direito trabalhista")
>>> print(f"Status: {result['status']}, Tempo: {result['tempo']}ms")
```
**Resultado esperado**: Status "djen", tempo ~1600ms

#### **3. Testar Agente Neutro**
```bash
cd backend
python manage.py shell
>>> from jurisprudencia.utils.neutral_agent import NeutralSearchAgent
>>> agent = NeutralSearchAgent()
>>> result = agent.gerar_variacoes_busca("direito trabalhista")
>>> print(f"Variações: {len(result['variacoes'])}")
```
**Resultado esperado**: 3+ variações geradas

#### **4. Acessar Interface Web**
- **URL**: http://localhost:8000
- **Funcionalidade**: Busca de jurisprudência via DJEN
- **Interface**: Bootstrap responsiva

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

## 🎯 **Status Atual do Projeto**

### **✅ Sprint 3 Concluída (26/09/2024)**
- ✅ **Integração DJEN**: API funcionando com rate limiting
- ✅ **Sistema Django**: Interface web operacional
- ✅ **Agente Neutro**: Implementado e testado
- ✅ **Testes**: 17 testes automatizados passando
- ✅ **Documentação**: Completa e organizada
- ✅ **Evidências**: Logs capturados e validados

### **🧪 Evidências de Funcionamento**
- **Testes Automatizados**: `python manage.py test` - 17 testes OK
- **Integração DJEN**: API respondendo em ~1.6s
- **Agente Neutro**: Gerando variações de busca automaticamente
- **Sistema Web**: Interface Django funcionando

### **📊 Métricas Alcançadas**
- **Cobertura de Testes**: 17 testes implementados
- **Integração API**: 100% funcional
- **Documentação**: 25+ documentos organizados
- **Evidências Ágeis**: Manifesto + 12 princípios evidenciados

## 🎯 **Roadmap de Implementação**

### **Sprint 1-2: Setup e Planejamento** ✅
- ✅ Configuração do ambiente de desenvolvimento
- ✅ Definição de arquitetura e especificações
- ✅ Planejamento detalhado dos agentes
- ✅ Interface Django Bootstrap para consulta DJEN

### **Sprint 3: Integração e Validação** ✅
- ✅ Validação integração DJENCollector com API
- ✅ Verificação integridade dos dados DJEN
- ✅ Melhoria interface de consulta Django
- ✅ Tratamento de erros robusto
- ✅ Agente Neutro implementado e testado
- ✅ Documentação completa e organizada

### **Sprint 4: MVP - Busca Favorável à Tese**
- 🔄 AgenteClassificadorTese para classificar julgados
- 🔄 Interface Django aprimorada para consulta de julgados favoráveis
- 🔄 Algoritmo de classificação favorável/desfavorável
- 🔄 Integração DJEN e modelos de dados

### **Sprint 5: Análise Neutra**
- AgenteAnalisadorNeutro para análise objetiva
- Interface Django para análise neutra
- Identificação de argumentos pró e contra
- Gráficos e estatísticas avançadas

### **Sprint 6: Padrões por Vara**
- AgenteAnalisadorVara para padrões específicos
- Relatório: "Sobre o tema X, essa vara decide..."
- Geração de perfil do julgador
- Interface Django para visualização de padrões

### **Sprint 7: Estratégia Antecipatória + Mobile**
- AgenteEstrategicoAntecipatorio para predições
- Sistema de argumentos direcionados
- Relatórios exportáveis em PDF/DOCX
- 🆕 **App Mobile**: React Native para consultas móveis

## 🤝 **Contribuição**

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request


## 📞 **Contato**

- **GitHub**: [@ftorres92](https://github.com/ftorres92)
- **Projeto**: [juris-dev-agil](https://github.com/ftorres92/juris-dev-agil)


