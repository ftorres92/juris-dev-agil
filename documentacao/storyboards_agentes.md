# 🎬 Storyboards dos Agentes - Sistema de Jurisprudência IA

## 📋 **Storyboard 1: Busca de Jurisprudência Favorável à Tese**

### **Cenário**: Dr. Carlos Silva busca julgados favoráveis à sua tese sobre "prescrição intercorrente"

**Fluxo de Interação:**

1. **Entrada do Usuário**
   - Dr. Carlos acessa o sistema
   - Preenche formulário: "Tema: Prescrição intercorrente"
   - Descreve sua tese: "A prescrição intercorrente não se aplica quando há reconhecimento de vício..."
   - Seleciona tribunais: STJ, TRF-3, TJ-SP

2. **Processamento do Agente Classificador**
   - Sistema coleta julgados do DJEN sobre o tema
   - AgenteClassificadorTese analisa cada julgado
   - Classifica como favorável/desfavorável à tese específica
   - Calcula score de favorabilidade (0-100%)

3. **Resultado para o Usuário**
   - Lista de 15 julgados favoráveis (score > 70%)
   - Explicação da classificação para cada julgado
   - Identificação de precedentes fortes (STJ, STF)
   - Opção de export em PDF

**Exemplo de Explicação do Agente:**
> "Este julgado foi classificado como 85% favorável à sua tese porque reconhece que a prescrição intercorrente não se aplica quando há reconhecimento de vício processual, corroborando seu argumento principal."

---

## 📊 **Storyboard 2: Análise Neutra da Jurisprudência**

### **Cenário**: Ana Santos quer entender a jurisprudência real sobre "responsabilidade civil do Estado"

**Fluxo de Interação:**

1. **Entrada do Usuário**
   - Ana acessa "Análise Neutra"
   - Informa tema: "Responsabilidade civil do Estado"
   - Define período: últimos 2 anos
   - Seleciona tribunais: STJ, STF, TRF-1

2. **Processamento do Agente Analisador Neutro**
   - Coleta ampla de julgados sobre o tema
   - AgenteAnalisadorNeutro analisa sem viés
   - Identifica argumentos pró e contra
   - Calcula tendência geral da jurisprudência

3. **Resultado para o Usuário**
   - Dashboard com gráfico de tendência (60% favorável, 25% contrária, 15% neutra)
   - Lista de argumentos principais pró e contra
   - Timeline mostrando evolução da jurisprudência
   - Identificação de mudanças recentes

**Exemplo de Análise do Agente:**
> "A jurisprudência sobre responsabilidade civil do Estado mostra tendência majoritariamente favorável (60%), com argumentos principais pró: dever de indenizar por danos causados, e contra: necessidade de comprovação de nexo causal."

---

## 🏛️ **Storyboard 3: Análise de Padrões por Vara**

### **Cenário**: Dr. Carlos quer entender como a 1ª Vara Cível de São Paulo julga "danos morais"

**Fluxo de Interação:**

1. **Entrada do Usuário**
   - Dr. Carlos acessa "Padrões por Vara"
   - Seleciona: 1ª Vara Cível de São Paulo
   - Define tema: "Danos morais"
   - Período: últimos 3 anos

2. **Processamento do Agente Analisador Vara**
   - Coleta julgados específicos da vara
   - AgenteAnalisadorVara identifica padrões
   - Analisa perfil do julgador
   - Calcula tendência da vara

3. **Resultado para o Usuário**
   - Relatório: "Sobre danos morais, a 1ª Vara Cível de SP decide da seguinte forma..."
   - Perfil do julgador: "Tendência conservadora, valor médio de R$ 5.000"
   - Padrões identificados: "Requer prova robusta, valor moderado"
   - Comparação com outras varas

**Exemplo de Relatório do Agente:**
> "A 1ª Vara Cível de São Paulo apresenta padrão conservador em danos morais, com valor médio de R$ 5.000 e exigência de prova robusta do dano. Tendência: 70% favorável quando há prova documental."

---

## 🎯 **Storyboard 4: Estratégia Antecipatória**

### **Cenário**: Dr. Carlos quer antecipar como a 2ª Vara Trabalhista julgará seu caso de "horas extras"

**Fluxo de Interação:**

1. **Entrada do Usuário**
   - Dr. Carlos acessa "Estratégia Antecipatória"
   - Upload do caso: "Horas extras não pagas - 2 anos"
   - Seleciona vara: 2ª Vara Trabalhista de São Paulo
   - Informa contexto: "Empresa de grande porte, sindicato ativo"

2. **Processamento do Agente Estratégico Antecipatório**
   - Analisa histórico da vara em casos similares
   - AgenteEstrategicoAntecipatorio calcula probabilidade
   - Identifica riscos específicos
   - Gera estratégia personalizada

3. **Resultado para o Usuário**
   - Probabilidade de sucesso: 75%
   - Riscos identificados: "Prova de jornada, acordo coletivo"
   - Estratégia recomendada: "Focar em prova testemunhal, evitar acordo coletivo"
   - Argumentos direcionados para a vara

**Exemplo de Estratégia do Agente:**
> "Probabilidade de sucesso: 75%. Riscos: acordo coletivo pode limitar valor. Estratégia: focar em prova testemunhal robusta e evitar menção ao acordo coletivo. Argumentos direcionados: jurisprudência do TST sobre horas extras."

---

## 🔄 **Fluxo de Integração entre Agentes**

### **Cenário Completo**: Dr. Carlos faz análise completa de um caso

1. **Busca Favorável**: Encontra 20 julgados favoráveis à sua tese
2. **Análise Neutra**: Entende que jurisprudência é 60% favorável
3. **Padrões da Vara**: Descobre que a vara tem tendência conservadora
4. **Estratégia Antecipatória**: Recebe probabilidade de 75% de sucesso

**Resultado Integrado:**
- Dr. Carlos tem visão completa e estratégica
- Argumentos sólidos baseados em jurisprudência favorável
- Estratégia personalizada para a vara específica
- Maior confiança e chances de sucesso

---

## 🎨 **Elementos Visuais dos Storyboards**

### **Interface do Agente Classificador**
- Ícone: 🔍 (lupa com IA)
- Cores: Azul (confiança, precisão)
- Feedback: "Analisando 150 julgados... 85% favoráveis encontrados"

### **Interface do Agente Analisador Neutro**
- Ícone: ⚖️ (balança neutra)
- Cores: Verde (objetividade, clareza)
- Feedback: "Tendência majoritária: 60% favorável"

### **Interface do Agente Analisador Vara**
- Ícone: 🏛️ (tribunal)
- Cores: Roxo (autoridade, especialização)
- Feedback: "Padrão identificado: tendência conservadora"

### **Interface do Agente Estratégico**
- Ícone: 🎯 (alvo estratégico)
- Cores: Laranja (energia, ação)
- Feedback: "Probabilidade de sucesso: 75%"

---

## 📱 **Fluxo Mobile/Desktop**

### **Desktop (Advogado Experiente)**
- Dashboard completo com todos os agentes
- Análises detalhadas e relatórios
- Export em PDF/DOCX
- Comparação entre varas

### **Mobile (Advogado em Campo)**
- Busca rápida de jurisprudência favorável
- Notificações de novos julgados
- Consulta de padrões por vara
- Estratégia resumida

---

**Criado em:** 23/09/2024  
**Foco:** Ideação e Prototipagem  
**Próximo:** Protótipo de baixa fidelidade
