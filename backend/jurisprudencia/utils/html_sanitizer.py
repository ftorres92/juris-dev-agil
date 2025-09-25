from __future__ import annotations

import re
from typing import Iterable

import bleach


ALLOWED_TAGS: Iterable[str] = (
    'b', 'strong', 'i', 'em', 'u',
    'p', 'br', 'span', 'div',
    'ul', 'ol', 'li',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
)

ALLOWED_ATTRS = {
    '*': [],
    'p': ['align'],
    'table': ['border'],
}


_BR_CLOSING = re.compile(r"</br>", flags=re.IGNORECASE)


def normalize_html_fragment(html: str) -> str:
    if not html:
        return html
    # Corrige tags de quebra de linha malformadas
    html = _BR_CLOSING.sub('<br/>', html)
    # Opcional: normalizar <br> simples para <br/>
    html = html.replace('<br>', '<br/>').replace('<BR>', '<br/>')
    return html


def sanitize_fragment(html: str) -> str:
    """Sanitiza HTML mantendo tags básicas e tabelas simples.

    Remove atributos não permitidos e corrige pequenas malformações de <br>.
    """
    if not html:
        return ''
    normalized = normalize_html_fragment(html)
    cleaned = bleach.clean(
        normalized,
        tags=list(ALLOWED_TAGS),
        attributes=ALLOWED_ATTRS,
        strip=True,
    )
    return cleaned


