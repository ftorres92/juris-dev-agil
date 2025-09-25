# 🔗 Especificação de Views Django - Sistema de Jurisprudência

> **Objetivo:** Definir as views Django e templates para o sistema SaaS de análise de jurisprudência, baseado na API de intimações do PJE.

## 📋 Estrutura de Dados da API

### **Resposta Padrão da API**
```json
{
  "status": "string",
  "message": "string", 
  "count": 0,
  "items": [
    {
      "id": 0,
      "data_disponibilizacao": "string",
      "siglaTribunal": "string",
      "tipoComunicacao": "string",
      "nomeOrgao": "string",
      "texto": "string",
      "numero_processo": "string",
      "meio": "string",
      "link": "string",
      "tipoDocumento": "string",
      "nomeClasse": "string",
      "codigoClasse": "string",
      "numeroComunicacao": 0,
      "ativo": true,
      "hash": "string",
      "datadisponibilizacao": "string",
      "meiocompleto": "string",
      "numeroprocessocommascara": "string",
      "destinatarios": [
        {
          "nome": "string",
          "polo": "string",
          "comunicacao_id": 0
        }
      ],
      "destinatarioadvogados": [
        {
          "id": 0,
          "comunicacao_id": 0,
          "advogado_id": 0,
          "created_at": "string",
          "updated_at": "string",
          "advogado": {
            "id": 0,
            "nome": "string",
            "numero_oab": "string",
            "uf_oab": "string"
          }
        }
      ]
    }
  ]
}
```

## 🛣️ Views Django a Implementar

### **1. Página Principal - Dashboard**
```python
# URL: /
# View: dashboard_view
# Template: dashboard.html
# Descrição: Página inicial com métricas e análises recentes
```

### **2. Busca de Jurisprudência**
```python
# URL: /buscar/
# View: buscar_jurisprudencia_view
# Template: buscar_jurisprudencia.html
# Descrição: Formulário de busca e resultados
```

**Campos do Formulário:**
- `termo` (CharField, obrigatório): Termo de busca
- `sigla_tribunal` (ChoiceField, opcional): Tribunal
- `data_inicio` (DateField, opcional): Data inicial
- `data_fim` (DateField, opcional): Data final
- `numero_processo` (CharField, opcional): Número do processo
- `tipo_documento` (ChoiceField, opcional): Tipo de documento

### **3. Resultados da Busca**
```python
# URL: /resultados/
# View: resultados_view
# Template: resultados.html
# Descrição: Lista de julgados encontrados
```

### **4. Análise com Agentes**
```python
# URL: /analisar/
# View: analisar_jurisprudencia_view
# Template: analisar_jurisprudencia.html
# Descrição: Solicita análise pelos agentes de IA
```

**Campos do Formulário:**
- `termo` (CharField, obrigatório): Termo de busca
- `filtros` (JSONField): Filtros adicionais
- `agentes` (MultipleChoiceField): Agentes a utilizar
- `limite` (IntegerField): Limite de julgados

### **5. Status da Análise**
```python
# URL: /analise/<analise_id>/status/
# View: status_analise_view
# Template: status_analise.html
# Descrição: Acompanha progresso da análise
```

### **6. Resultados da Análise**
```python
# URL: /analise/<analise_id>/resultados/
# View: resultados_analise_view
# Template: resultados_analise.html
# Descrição: Visualiza resultados dos agentes
```

## 🔧 Implementação Django

### **1. Models Django**

```python
# backend/jurisprudencia/models.py

from django.db import models
from django.contrib.auth.models import User
import uuid

class AnaliseJurisprudencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    termo = models.CharField(max_length=500)
    filtros = models.JSONField(default=dict)
    agentes_solicitados = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluida', 'Concluída'),
        ('erro', 'Erro')
    ], default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    resultados = models.JSONField(default=dict)
    erro = models.TextField(blank=True, null=True)

class Julgado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analise = models.ForeignKey(AnaliseJurisprudencia, on_delete=models.CASCADE, related_name='julgados')
    id_externo = models.IntegerField()  # ID da API externa
    data_disponibilizacao = models.DateTimeField()
    sigla_tribunal = models.CharField(max_length=10)
    tipo_comunicacao = models.CharField(max_length=50)
    nome_orgao = models.CharField(max_length=200)
    texto = models.TextField()
    numero_processo = models.CharField(max_length=50)
    meio = models.CharField(max_length=10)
    link = models.URLField()
    tipo_documento = models.CharField(max_length=50)
    nome_classe = models.CharField(max_length=200)
    codigo_classe = models.CharField(max_length=20)
    numero_comunicacao = models.IntegerField()
    ativo = models.BooleanField(default=True)
    hash_externo = models.CharField(max_length=100)
    data_disponibilizacao_str = models.CharField(max_length=50)
    meio_completo = models.CharField(max_length=100)
    numero_processo_mascara = models.CharField(max_length=50)
    
    # Campos de análise dos agentes
    favorabilidade_score = models.FloatField(null=True, blank=True)
    classificacao = models.CharField(max_length=20, choices=[
        ('favoravel', 'Favorável'),
        ('desfavoravel', 'Desfavorável'),
        ('neutro', 'Neutro')
    ], null=True, blank=True)
    argumentos_chave = models.JSONField(default=list)
    precedentes = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-data_disponibilizacao']
```

### **2. Forms Django**

```python
# backend/jurisprudencia/forms.py

from django import forms
from .models import AnaliseJurisprudencia

class BuscaJurisprudenciaForm(forms.Form):
    termo = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o termo de busca...'
        })
    )
    sigla_tribunal = forms.ChoiceField(
        choices=[
            ('', 'Todos os tribunais'),
            ('TRF1', 'TRF1'),
            ('TRF2', 'TRF2'),
            ('TRF3', 'TRF3'),
            ('TRF4', 'TRF4'),
            ('TRF5', 'TRF5'),
            ('TRF6', 'TRF6'),
            ('STJ', 'STJ'),
            ('STF', 'STF'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    numero_processo = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número do processo...'
        })
    )

class AnaliseJurisprudenciaForm(forms.ModelForm):
    agentes = forms.MultipleChoiceField(
        choices=[
            ('classificador_tese', 'Classificador por Tese'),
            ('analisador_neutro', 'Analisador Neutro'),
            ('analisador_vara', 'Analisador por Vara'),
            ('estrategico_antecipatorio', 'Estratégico Antecipatório'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = AnaliseJurisprudencia
        fields = ['termo', 'filtros', 'agentes_solicitados', 'limite']
        widgets = {
            'termo': forms.TextInput(attrs={'class': 'form-control'}),
            'filtros': forms.HiddenInput(),
            'limite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 500})
        }
```

### **3. Views Django**

```python
# backend/jurisprudencia/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import AnaliseJurisprudencia, Julgado
from .forms import BuscaJurisprudenciaForm, AnaliseJurisprudenciaForm
from .utils.djen import DJENCollector
from .tasks import processar_analise_jurisprudencia

def dashboard_view(request):
    """
    Página inicial com métricas e análises recentes
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Análises recentes do usuário
    analises_recentes = AnaliseJurisprudencia.objects.filter(
        usuario=request.user
    ).order_by('-data_criacao')[:5]
    
    # Métricas básicas
    total_analises = AnaliseJurisprudencia.objects.filter(usuario=request.user).count()
    analises_concluidas = AnaliseJurisprudencia.objects.filter(
        usuario=request.user, 
        status='concluida'
    ).count()
    
    context = {
        'analises_recentes': analises_recentes,
        'total_analises': total_analises,
        'analises_concluidas': analises_concluidas,
    }
    
    return render(request, 'jurisprudencia/dashboard.html', context)

@login_required
def buscar_jurisprudencia_view(request):
    """
    Busca jurisprudência por termo e filtros
    """
    form = BuscaJurisprudenciaForm()
    resultados = None
    houve_busca = False
    
    if request.method == 'POST':
        form = BuscaJurisprudenciaForm(request.POST)
        if form.is_valid():
            # Usar DJENCollector para buscar dados
            collector = DJENCollector()
            
            # Montar parâmetros para a API externa
            params = {
                'termo': form.cleaned_data['termo'],
                'siglaTribunal': form.cleaned_data.get('sigla_tribunal'),
                'dataInicio': form.cleaned_data.get('data_inicio'),
                'dataFim': form.cleaned_data.get('data_fim'),
                'numeroProcesso': form.cleaned_data.get('numero_processo'),
            }
            
            # Remover parâmetros None
            params = {k: v for k, v in params.items() if v is not None}
            
            try:
                resultados = collector.search(params)
                houve_busca = True
            except Exception as e:
                messages.error(request, f'Erro ao buscar jurisprudência: {str(e)}')
    
    context = {
        'form': form,
        'resultados': resultados,
        'houve_busca': houve_busca,
    }
    
    return render(request, 'jurisprudencia/buscar_jurisprudencia.html', context)

@login_required
def analisar_jurisprudencia_view(request):
    """
    Solicita análise pelos agentes de IA
    """
    if request.method == 'POST':
        form = AnaliseJurisprudenciaForm(request.POST)
        if form.is_valid():
            # Criar análise
            analise = AnaliseJurisprudencia.objects.create(
                usuario=request.user,
                termo=form.cleaned_data['termo'],
                filtros=form.cleaned_data.get('filtros', {}),
                agentes_solicitados=form.cleaned_data['agentes'],
                status='pendente'
            )
            
            # Enfileirar tarefa de processamento
            processar_analise_jurisprudencia.delay(str(analise.id))
            
            messages.success(request, 'Análise solicitada com sucesso!')
            return redirect('status_analise', analise_id=analise.id)
    else:
        form = AnaliseJurisprudenciaForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'jurisprudencia/analisar_jurisprudencia.html', context)

@login_required
def status_analise_view(request, analise_id):
    """
    Acompanha progresso da análise
    """
    analise = get_object_or_404(AnaliseJurisprudencia, id=analise_id, usuario=request.user)
    
    context = {
        'analise': analise,
    }
    
    return render(request, 'jurisprudencia/status_analise.html', context)

@login_required
def resultados_analise_view(request, analise_id):
    """
    Visualiza resultados dos agentes
    """
    analise = get_object_or_404(AnaliseJurisprudencia, id=analise_id, usuario=request.user)
    
    if analise.status != 'concluida':
        messages.warning(request, 'Análise ainda não concluída')
        return redirect('status_analise', analise_id=analise_id)
    
    # Paginar resultados
    julgados = analise.julgados.all()
    paginator = Paginator(julgados, 25)
    page = request.GET.get('pagina', 1)
    
    try:
        julgados_paginados = paginator.page(page)
    except:
        julgados_paginados = paginator.page(1)
    
    context = {
        'analise': analise,
        'julgados': julgados_paginados,
        'total_julgados': julgados.count(),
    }
    
    return render(request, 'jurisprudencia/resultados_analise.html', context)

def status_analise_ajax(request, analise_id):
    """
    AJAX endpoint para verificar status da análise
    """
    analise = get_object_or_404(AnaliseJurisprudencia, id=analise_id, usuario=request.user)
    
    return JsonResponse({
        'status': analise.status,
        'data_criacao': analise.data_criacao.isoformat(),
        'data_conclusao': analise.data_conclusao.isoformat() if analise.data_conclusao else None,
        'erro': analise.erro,
    })
```

### **4. URLs Django**

```python
# backend/jurisprudencia/urls.py

from django.urls import path
from .views import (
    dashboard_view,
    buscar_jurisprudencia_view,
    analisar_jurisprudencia_view,
    status_analise_view,
    resultados_analise_view,
    status_analise_ajax
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('buscar/', buscar_jurisprudencia_view, name='buscar_jurisprudencia'),
    path('analisar/', analisar_jurisprudencia_view, name='analisar_jurisprudencia'),
    path('analise/<uuid:analise_id>/status/', status_analise_view, name='status_analise'),
    path('analise/<uuid:analise_id>/resultados/', resultados_analise_view, name='resultados_analise'),
    path('analise/<uuid:analise_id>/status/ajax/', status_analise_ajax, name='status_analise_ajax'),
]
```

### **5. Tasks Celery**

```python
# backend/jurisprudencia/tasks.py

from celery import shared_task
from .models import AnaliseJurisprudencia, Julgado
from .utils.djen import DJENCollector
from .utils.agentes import AgenteClassificadorTese, AgenteAnalisadorNeutro

@shared_task
def processar_analise_jurisprudencia(analise_id):
    """
    Processa análise de jurisprudência com os agentes solicitados
    """
    try:
        analise = AnaliseJurisprudencia.objects.get(id=analise_id)
        analise.status = 'processando'
        analise.save()
        
        # Buscar dados no DJEN
        collector = DJENCollector()
        params = {
            'termo': analise.termo,
            **analise.filtros
        }
        
        resultado = collector.search(params)
        julgados_data = resultado.get('items', [])
        
        # Salvar julgados
        for item in julgados_data:
            Julgado.objects.create(
                analise=analise,
                id_externo=item.get('id'),
                data_disponibilizacao=item.get('data_disponibilizacao'),
                sigla_tribunal=item.get('siglaTribunal'),
                tipo_comunicacao=item.get('tipoComunicacao'),
                nome_orgao=item.get('nomeOrgao'),
                texto=item.get('texto'),
                numero_processo=item.get('numero_processo'),
                meio=item.get('meio'),
                link=item.get('link'),
                tipo_documento=item.get('tipoDocumento'),
                nome_classe=item.get('nomeClasse'),
                codigo_classe=item.get('codigoClasse'),
                numero_comunicacao=item.get('numeroComunicacao'),
                ativo=item.get('ativo', True),
                hash_externo=item.get('hash'),
                data_disponibilizacao_str=item.get('datadisponibilizacao'),
                meio_completo=item.get('meiocompleto'),
                numero_processo_mascara=item.get('numeroprocessocommascara')
            )
        
        # Processar com agentes solicitados
        resultados = {}
        
        if 'classificador_tese' in analise.agentes_solicitados:
            classificador = AgenteClassificadorTese()
            resultados['classificador_tese'] = classificador.processar(analise)
        
        if 'analisador_neutro' in analise.agentes_solicitados:
            analisador = AgenteAnalisadorNeutro()
            resultados['analisador_neutro'] = analisador.processar(analise)
        
        # Atualizar análise
        analise.status = 'concluida'
        analise.resultados = resultados
        analise.save()
        
    except Exception as e:
        analise.status = 'erro'
        analise.erro = str(e)
        analise.save()
        raise e
```

## 🔄 Fluxo de Integração

### **1. Busca Simples**
```
Usuário → Formulário Django → DJENCollector → API Externa → Template com Resultados
```

### **2. Análise com Agentes**
```
Usuário → Formulário Django → Celery Task → Agentes → Página de Status → Resultados
```

### **3. Acompanhamento de Status**
```
Usuário → Página de Status → AJAX → Status da Análise → Atualização em Tempo Real
```

### **4. Visualização de Resultados**
```
Usuário → Página de Resultados → Template com Julgados → Paginação → Exportação
```

## 📊 Exemplos de Uso

### **Acesso ao Sistema**
```
http://localhost:8000/                    # Dashboard
http://localhost:8000/buscar/             # Busca de jurisprudência
http://localhost:8000/analisar/            # Análise com agentes
http://localhost:8000/analise/{id}/status/ # Status da análise
http://localhost:8000/analise/{id}/resultados/ # Resultados
```

### **Fluxo do Usuário**
1. **Login** → Dashboard com métricas
2. **Buscar** → Formulário de busca → Resultados
3. **Analisar** → Selecionar agentes → Solicitar análise
4. **Acompanhar** → Página de status com atualização em tempo real
5. **Visualizar** → Resultados com classificação dos agentes
6. **Exportar** → Download de relatórios em PDF/DOCX

## ✅ Critérios de Implementação

- [ ] Models Django criados
- [ ] Forms Django implementados
- [ ] Views Django funcionando
- [ ] URLs configuradas
- [ ] Templates HTML criados
- [ ] Tasks Celery implementadas
- [ ] Integração com DJENCollector
- [ ] Testes unitários
- [ ] Autenticação Django
- [ ] Rate limiting
- [ ] Cache Redis
- [ ] Logs estruturados
- [ ] Interface responsiva
- [ ] AJAX para atualizações em tempo real
- [ ] Exportação de relatórios
