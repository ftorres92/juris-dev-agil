from __future__ import annotations

from datetime import date
from typing import Iterable, List, Sequence

from django import forms

TRIBUNAIS_PADRAO: Sequence[str] = (
    'STF', 'STJ', 'TST', 'STM',
    'TRF1', 'TRF2', 'TRF3', 'TRF4', 'TRF5', 'TRF6',
    'TJAC', 'TJAL', 'TJAM', 'TJAP', 'TJBA', 'TJCE', 'TJDFT', 'TJES', 'TJGO', 'TJMA',
    'TJMG', 'TJMS', 'TJMT', 'TJPA', 'TJPB', 'TJPE', 'TJPI', 'TJRJ', 'TJRN', 'TJRO',
    'TJRR', 'TJRS', 'TJSC', 'TJSE', 'TJSP', 'TJTO',
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
