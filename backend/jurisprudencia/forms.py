from __future__ import annotations

from datetime import date
from typing import Iterable, List, Sequence

from django import forms

TRIBUNAIS_PADRAO: Sequence[str] = (
    # Superiores e Conselhos
    'STF', 'STJ', 'TST', 'TSE', 'STM', 'CSJT', 'CJF', 'CNJ', 'PJeCor', 'SEEU',

    # TRFs
    'TRF1', 'TRF2', 'TRF3', 'TRF4', 'TRF5', 'TRF6',

    # TRTs (1 a 24)
    'TRT1', 'TRT2', 'TRT3', 'TRT4', 'TRT5', 'TRT6', 'TRT7', 'TRT8', 'TRT9',
    'TRT10', 'TRT11', 'TRT12', 'TRT13', 'TRT14', 'TRT15', 'TRT16', 'TRT17', 'TRT18',
    'TRT19', 'TRT20', 'TRT21', 'TRT22', 'TRT23', 'TRT24',

    # TREs (todas as UFs)
    'TRE-AC', 'TRE-AL', 'TRE-AM', 'TRE-AP', 'TRE-BA', 'TRE-CE', 'TRE-DF', 'TRE-ES',
    'TRE-GO', 'TRE-MA', 'TRE-MG', 'TRE-MS', 'TRE-MT', 'TRE-PA', 'TRE-PB', 'TRE-PE',
    'TRE-PI', 'TRE-PR', 'TRE-RJ', 'TRE-RN', 'TRE-RO', 'TRE-RR', 'TRE-RS', 'TRE-SC',
    'TRE-SE', 'TRE-SP', 'TRE-TO',

    # TJs (todas as UFs)
    'TJAC', 'TJAL', 'TJAM', 'TJAP', 'TJBA', 'TJCE', 'TJDFT', 'TJES', 'TJGO', 'TJMA',
    'TJMG', 'TJMS', 'TJMT', 'TJPA', 'TJPB', 'TJPE', 'TJPI', 'TJRJ', 'TJRN', 'TJRO',
    'TJRR', 'TJRS', 'TJSC', 'TJSE', 'TJSP', 'TJTO',

    # TJMs (estaduais)
    'TJMMG', 'TJMRS', 'TJMSP',
)

TIPOS_DECISAO_PADRAO = (
    ('', 'Qualquer tipo'),
    ('acordao', 'Acórdão'),
    ('monocratico', 'Monocrático'),
    ('despacho', 'Despacho'),
)


class DjenSearchForm(forms.Form):
    termo = forms.CharField(max_length=255)
    tribunais = forms.MultipleChoiceField(choices=[(t, t) for t in TRIBUNAIS_PADRAO])
    periodo_inicio = forms.DateField(required=False)
    periodo_fim = forms.DateField(required=False)
    tipo_decisao = forms.ChoiceField(choices=TIPOS_DECISAO_PADRAO, required=False)
    limite = forms.IntegerField(min_value=1, max_value=200, required=False, initial=25)

    def clean_tribunais(self) -> List[str]:
        tribunais: Iterable[str] = self.cleaned_data['tribunais']
        tribunais_list = [t.strip() for t in tribunais if t.strip()]
        if not tribunais_list:
            raise forms.ValidationError('Selecione pelo menos um tribunal.')
        return tribunais_list

    def clean(self) -> dict:
        cleaned_data = super().clean()
        periodo_inicio: date | None = cleaned_data.get('periodo_inicio')
        periodo_fim: date | None = cleaned_data.get('periodo_fim')

        if periodo_inicio and periodo_fim and periodo_inicio > periodo_fim:
            self.add_error('periodo_fim', 'O período final deve ser posterior ao inicial.')

        limite = cleaned_data.get('limite')
        if limite is None:
            cleaned_data['limite'] = 25

        return cleaned_data


class IntimacoesBuscaForm(forms.Form):
    """Formulário para consulta às intimações (DJEN proxy).

    Suporta três modos de busca:
    - por_oab: numero_oab + uf_oab (e datas opcionais)
    - por_oab_string: oab_string (ex.: 'SP07749')
    - por_nome: nome_advogado e/ou nome_parte, com filtros opcionais
    """

    MODO_CHOICES = (
        ("por_oab", "Por OAB + UF"),
        ("por_oab_string", "Por OAB como string"),
        ("por_nome", "Por nome (advogado/parte)"),
    )

    modo = forms.ChoiceField(choices=MODO_CHOICES, initial="por_oab")

    # por_oab
    numero_oab = forms.CharField(required=False, max_length=20)
    uf_oab = forms.CharField(required=False, max_length=2)

    # por_oab_string
    oab_string = forms.CharField(required=False, max_length=20)

    # por_nome
    nome_advogado = forms.CharField(required=False, max_length=255)
    nome_parte = forms.CharField(required=False, max_length=255)
    sigla_tribunal = forms.CharField(required=False, max_length=10)

    # filtros comuns
    data_inicio = forms.DateField(required=False)
    data_fim = forms.DateField(required=False)
    pagina = forms.IntegerField(required=False, min_value=1)
    itens_por_pagina = forms.IntegerField(required=False, min_value=1, max_value=100)

    def clean(self) -> dict:
        cleaned = super().clean()
        modo = cleaned.get("modo")

        if modo == "por_oab":
            if not cleaned.get("numero_oab") or not cleaned.get("uf_oab"):
                self.add_error("numero_oab", "Informe o número da OAB e a UF.")
                self.add_error("uf_oab", "Informe a UF da OAB.")
        elif modo == "por_oab_string":
            if not cleaned.get("oab_string"):
                self.add_error("oab_string", "Informe a OAB como string (ex.: SP07749).")
        elif modo == "por_nome":
            if not cleaned.get("nome_advogado") and not cleaned.get("nome_parte"):
                self.add_error("nome_advogado", "Informe ao menos um campo: advogado ou parte.")

        di = cleaned.get("data_inicio")
        df = cleaned.get("data_fim")
        if di and df and di > df:
            self.add_error("data_fim", "Data fim deve ser posterior à data início.")

        return cleaned
