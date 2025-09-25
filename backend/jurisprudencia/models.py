from hashlib import sha256
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import uuid


class BaseModel(models.Model):
    """
    Modelo base com campos comuns para auditoria
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_criados",
        verbose_name="Criado por"
    )
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        should_full_clean = kwargs.pop('full_clean', True)
        if should_full_clean:
            update_fields = kwargs.get('update_fields')
            exclude = list(update_fields) if update_fields else None
            self.full_clean(exclude=exclude, validate_unique=False)
        super().save(*args, **kwargs)


class Julgado(BaseModel):
    """
    Modelo para armazenar julgados coletados do DJEN
    """
    numero_processo = models.CharField(max_length=50, verbose_name="Número do processo")
    titulo = models.TextField(verbose_name="Título/Ementa")
    conteudo = models.TextField(verbose_name="Conteúdo completo do julgado")
    data_publicacao = models.DateField(verbose_name="Data de publicação")
    
    # Informações do tribunal
    tribunal = models.CharField(max_length=100, verbose_name="Tribunal")
    vara = models.CharField(max_length=255, blank=True, null=True, verbose_name="Vara")
    comarca = models.CharField(max_length=255, blank=True, null=True, verbose_name="Comarca")
    relator = models.CharField(max_length=255, blank=True, null=True, verbose_name="Relator")
    
    # Metadados do DJEN
    djen_id = models.CharField(max_length=100, unique=True, verbose_name="ID no DJEN")
    url_original = models.URLField(blank=True, null=True, verbose_name="URL original")
    
    # Controle de processamento
    processado = models.BooleanField(default=False, verbose_name="Processado pelos agentes")
    hash_conteudo = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        editable=False,
        verbose_name="Hash do conteúdo"
    )
    
    class Meta:
        verbose_name = "Julgado"
        verbose_name_plural = "Julgados"
        ordering = ['-data_publicacao']
        indexes = [
            models.Index(fields=['tribunal', 'data_publicacao']),
            models.Index(fields=['numero_processo']),
            models.Index(fields=['djen_id']),
        ]

    def __str__(self):
        return f"{self.numero_processo} - {self.tribunal}"

    def save(self, *args, **kwargs):
        if not self.hash_conteudo and self.conteudo:
            self.hash_conteudo = sha256(self.conteudo.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)


class AnaliseJurisprudenciaTese(BaseModel):
    """
    Análise de jurisprudência favorável a uma tese específica
    Baseado no Cenário 1 dos storyboards
    """
    tese_juridica = models.TextField(verbose_name="Tese jurídica analisada")
    termos_busca = models.JSONField(default=list, blank=True, verbose_name="Termos de busca utilizados")
    
    # Parâmetros da análise
    filtros_aplicados = models.JSONField(default=dict, blank=True, verbose_name="Filtros aplicados na busca")
    periodo_analise_inicio = models.DateField(verbose_name="Início do período analisado")
    periodo_analise_fim = models.DateField(verbose_name="Fim do período analisado")
    
    # Resultados da análise
    total_julgados_encontrados = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Total de julgados encontrados"
    )
    total_julgados_favoraveis = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Total de julgados favoráveis"
    )
    percentual_favorabilidade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Percentual de favorabilidade"
    )
    
    # Análise qualitativa
    argumentos_favoraveis = models.JSONField(default=list, blank=True, verbose_name="Principais argumentos favoráveis")
    precedentes_fortes = models.JSONField(default=list, blank=True, verbose_name="Precedentes de tribunais superiores")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações da análise")
    
    # Status da análise
    status = models.CharField(
        max_length=20,
        choices=[
            ('processando', 'Processando'),
            ('concluida', 'Concluída'),
            ('erro', 'Erro'),
        ],
        default='processando',
        verbose_name="Status"
    )
    
    # Relacionamentos
    julgados_favoraveis = models.ManyToManyField(
        Julgado,
        through='JulgadoFavoravel',
        related_name='analises_favoraveis',
        verbose_name="Julgados favoráveis"
    )
    
    class Meta:
        verbose_name = "Análise de Jurisprudência - Tese"
        verbose_name_plural = "Análises de Jurisprudência - Teses"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status', 'criado_em']),
            models.Index(fields=['percentual_favorabilidade']),
        ]
    
    def __str__(self):
        return f"Análise: {self.tese_juridica[:100]}..."

    def clean(self):
        super().clean()
        if self.periodo_analise_inicio and self.periodo_analise_fim:
            if self.periodo_analise_inicio > self.periodo_analise_fim:
                raise ValidationError("O início do período não pode ser posterior ao fim.")

        if self.total_julgados_favoraveis > self.total_julgados_encontrados:
            raise ValidationError("Julgados favoráveis não podem exceder o total encontrado.")

        if not (Decimal('0') <= Decimal(self.percentual_favorabilidade) <= Decimal('100')):
            raise ValidationError("Percentual de favorabilidade deve estar entre 0 e 100.")


class JulgadoFavoravel(BaseModel):
    """
    Tabela intermediária para relacionar julgados com análises de tese
    """
    analise = models.ForeignKey(AnaliseJurisprudenciaTese, on_delete=models.CASCADE)
    julgado = models.ForeignKey(Julgado, on_delete=models.CASCADE)
    
    score_favorabilidade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score de favorabilidade (0-100)"
    )
    justificativa = models.TextField(verbose_name="Justificativa do score")
    eh_precedente_forte = models.BooleanField(default=False, verbose_name="É precedente forte")
    argumentos_chave = models.JSONField(default=list, blank=True, verbose_name="Argumentos-chave identificados")
    
    class Meta:
        verbose_name = "Julgado Favorável"
        verbose_name_plural = "Julgados Favoráveis"
        unique_together = ['analise', 'julgado']
        indexes = [
            models.Index(fields=['score_favorabilidade']),
            models.Index(fields=['eh_precedente_forte']),
        ]
    
    def __str__(self):
        return f"{self.julgado.numero_processo} - Score: {self.score_favorabilidade}"


class AnaliseJurisprudenciaNeutra(BaseModel):
    """
    Análise neutra da jurisprudência sobre um tema
    Baseado no Cenário 2 dos storyboards
    """
    tema_juridico = models.TextField(verbose_name="Tema jurídico analisado")
    filtros_aplicados = models.JSONField(default=dict, blank=True, verbose_name="Filtros aplicados na busca")
    periodo_analise_inicio = models.DateField(verbose_name="Início do período analisado")
    periodo_analise_fim = models.DateField(verbose_name="Fim do período analisado")
    
    # Resultados quantitativos
    total_julgados_analisados = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Total de julgados analisados"
    )
    julgados_favoraveis = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Julgados favoráveis ao tema"
    )
    julgados_contrarios = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Julgados contrários ao tema"
    )
    julgados_neutros = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Julgados neutros"
    )
    
    # Análise qualitativa
    tendencia_majoritaria = models.CharField(
        max_length=20,
        choices=[
            ('favoravel', 'Favorável'),
            ('contraria', 'Contrária'),
            ('dividida', 'Dividida'),
            ('neutra', 'Neutra'),
        ],
        verbose_name="Tendência majoritária"
    )
    argumentos_pro = models.JSONField(default=list, blank=True, verbose_name="Principais argumentos pró")
    argumentos_contra = models.JSONField(default=list, blank=True, verbose_name="Principais argumentos contra")
    evolucao_temporal = models.JSONField(default=dict, blank=True, verbose_name="Evolução da tendência no tempo")
    
    # Julgados representativos
    julgados_representativos = models.ManyToManyField(
        Julgado,
        related_name='analises_neutras',
        verbose_name="Julgados representativos"
    )
    
    # Status da análise
    status = models.CharField(
        max_length=20,
        choices=[
            ('processando', 'Processando'),
            ('concluida', 'Concluída'),
            ('erro', 'Erro'),
        ],
        default='processando',
        verbose_name="Status"
    )
    
    class Meta:
        verbose_name = "Análise de Jurisprudência - Neutra"
        verbose_name_plural = "Análises de Jurisprudência - Neutras"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status', 'criado_em']),
            models.Index(fields=['tendencia_majoritaria']),
        ]
    
    def __str__(self):
        return f"Análise Neutra: {self.tema_juridico[:100]}..."

    def clean(self):
        super().clean()
        if self.periodo_analise_inicio and self.periodo_analise_fim:
            if self.periodo_analise_inicio > self.periodo_analise_fim:
                raise ValidationError("O início do período não pode ser posterior ao fim.")

        subtotal = self.julgados_favoraveis + self.julgados_contrarios + self.julgados_neutros
        if subtotal > self.total_julgados_analisados:
            raise ValidationError("A soma das classificações não pode exceder o total analisado.")


class PadroesVaraTribunal(BaseModel):
    """
    Análise de padrões de julgamento por vara/tribunal
    Baseado no Cenário 3 dos storyboards
    """
    tribunal = models.CharField(max_length=100, verbose_name="Tribunal")
    vara = models.CharField(max_length=255, blank=True, null=True, verbose_name="Vara específica")
    tema_juridico = models.TextField(verbose_name="Tema jurídico analisado")
    
    periodo_analise_inicio = models.DateField(verbose_name="Início do período analisado")
    periodo_analise_fim = models.DateField(verbose_name="Fim do período analisado")
    
    # Padrões identificados
    total_julgados_analisados = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Total de julgados analisados"
    )
    padroes_julgamento = models.JSONField(default=dict, blank=True, verbose_name="Padrões de julgamento identificados")
    perfil_julgador = models.JSONField(default=dict, blank=True, verbose_name="Perfil do julgador/órgão")
    precedentes_citados = models.JSONField(default=list, blank=True, verbose_name="Precedentes mais citados")
    
    # Estatísticas específicas
    valores_indenizacao = models.JSONField(default=dict, blank=True, verbose_name="Estatísticas de valores (se aplicável)")
    teses_aceitas = models.JSONField(default=list, blank=True, verbose_name="Teses frequentemente aceitas")
    teses_rejeitadas = models.JSONField(default=list, blank=True, verbose_name="Teses frequentemente rejeitadas")
    
    # Comparação com outros órgãos
    comparacao_outros_orgaos = models.JSONField(default=dict, blank=True, verbose_name="Comparação com outros órgãos")
    
    # Relacionamentos
    julgados_analisados = models.ManyToManyField(
        Julgado,
        related_name='padroes_vara',
        verbose_name="Julgados analisados"
    )
    
    # Status da análise
    status = models.CharField(
        max_length=20,
        choices=[
            ('processando', 'Processando'),
            ('concluida', 'Concluída'),
            ('erro', 'Erro'),
        ],
        default='processando',
        verbose_name="Status"
    )
    
    class Meta:
        verbose_name = "Padrões de Vara/Tribunal"
        verbose_name_plural = "Padrões de Varas/Tribunais"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['tribunal', 'vara']),
            models.Index(fields=['status', 'criado_em']),
        ]
        unique_together = ['tribunal', 'vara', 'tema_juridico', 'periodo_analise_inicio', 'periodo_analise_fim']
    
    def __str__(self):
        vara_info = f" - {self.vara}" if self.vara else ""
        return f"{self.tribunal}{vara_info}: {self.tema_juridico[:50]}..."

    def clean(self):
        super().clean()
        if self.periodo_analise_inicio and self.periodo_analise_fim:
            if self.periodo_analise_inicio > self.periodo_analise_fim:
                raise ValidationError("O início do período não pode ser posterior ao fim.")


class EstrategiaAntecipatoria(BaseModel):
    """
    Análise estratégica antecipatória para casos específicos
    Baseado no Cenário 4 dos storyboards
    """
    numero_processo = models.CharField(max_length=50, verbose_name="Número do processo")
    tribunal_destino = models.CharField(max_length=100, verbose_name="Tribunal/vara de destino")
    vara_destino = models.CharField(max_length=255, blank=True, null=True, verbose_name="Vara específica")
    
    # Documentos do caso
    documentos_caso = models.JSONField(default=list, blank=True, verbose_name="Documentos do caso analisados")
    resumo_caso = models.TextField(verbose_name="Resumo do caso")
    
    # Análise baseada nos padrões históricos
    padrao_vara_relacionado = models.ForeignKey(
        PadroesVaraTribunal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estrategias_baseadas',
        verbose_name="Padrão de vara relacionado"
    )
    
    # Resultados da análise
    probabilidade_sucesso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Probabilidade de sucesso (%)"
    )
    riscos_identificados = models.JSONField(default=list, blank=True, verbose_name="Riscos específicos identificados")
    estrategias_mitigacao = models.JSONField(default=list, blank=True, verbose_name="Estratégias de mitigação")
    
    # Recomendações estratégicas
    argumentos_direcionados = models.JSONField(default=list, blank=True, verbose_name="Argumentos direcionados para o órgão")
    precedentes_recomendados = models.JSONField(default=list, blank=True, verbose_name="Precedentes recomendados para citação")
    pontos_atencao = models.JSONField(default=list, blank=True, verbose_name="Pontos de atenção específicos")
    
    # Timeline de atuação
    cronograma_recomendado = models.JSONField(default=dict, blank=True, verbose_name="Cronograma recomendado")
    
    # Status da análise
    status = models.CharField(
        max_length=20,
        choices=[
            ('processando', 'Processando'),
            ('concluida', 'Concluída'),
            ('erro', 'Erro'),
        ],
        default='processando',
        verbose_name="Status"
    )
    
    # Validação posterior (para machine learning)
    resultado_real = models.CharField(
        max_length=20,
        choices=[
            ('favoravel', 'Favorável'),
            ('desfavoravel', 'Desfavorável'),
            ('parcial', 'Parcialmente favorável'),
            ('pendente', 'Pendente'),
        ],
        blank=True,
        null=True,
        verbose_name="Resultado real"
    )
    data_resultado = models.DateField(blank=True, null=True, verbose_name="Data do resultado")
    observacoes_resultado = models.TextField(blank=True, null=True, verbose_name="Observações sobre o resultado")
    
    class Meta:
        verbose_name = "Estratégia Antecipatória"
        verbose_name_plural = "Estratégias Antecipatórias"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['tribunal_destino', 'vara_destino']),
            models.Index(fields=['probabilidade_sucesso']),
            models.Index(fields=['status', 'criado_em']),
            models.Index(fields=['resultado_real']),
        ]
    
    def __str__(self):
        return f"Estratégia: {self.numero_processo} - {self.tribunal_destino}"

    def clean(self):
        super().clean()
        if self.probabilidade_sucesso is not None:
            if not (Decimal('0') <= Decimal(self.probabilidade_sucesso) <= Decimal('100')):
                raise ValidationError("Probabilidade de sucesso deve estar entre 0 e 100.")
