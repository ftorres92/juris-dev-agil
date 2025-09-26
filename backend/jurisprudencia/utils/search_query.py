from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import List, Tuple


def normalize_text(value: str) -> str:
    value = unicodedata.normalize('NFKD', value)
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return value.lower().strip()


@dataclass(frozen=True)
class ParsedQuery:
    phrases: Tuple[str, ...]           # "frase exata"
    required_terms: Tuple[str, ...]    # termos com AND implícito
    optional_terms: Tuple[str, ...]    # termos em OR explícito
    excluded_terms: Tuple[str, ...]    # -termo


_QUOTE_RE = re.compile(r'"([^"]+)"')

# Stopwords PT básicas para evitar matches irrelevantes (ex.: "de", "e", "do")
STOPWORDS_PT = {
    'a','à','às','ao','aos','as','o','os','um','uma','uns','umas',
    'de','da','das','do','dos','d','e','é','em','no','nos','na','nas','num','numa','nuns','numas',
    'por','para','pra','pro','com','sem','sob','sobre','entre','até','após','antes','contra','desde','trás',
    'que','se','sua','seu','suas','seus','ela','ele','elas','eles','nosso','nossa','nossos','nossas',
    'ou','onde','quando','como','qual','quais','mais','menos','muito','muita','muitos','muitas',
}


def parse_query(raw: str) -> ParsedQuery:
    if not raw:
        return ParsedQuery((), (), (), ())

    tokens: List[str] = []
    phrases = [m.group(1).strip() for m in _QUOTE_RE.finditer(raw)]
    cleaned = _QUOTE_RE.sub(' ', raw)
    for part in re.split(r'\s+', cleaned.strip()):
        if not part:
            continue
        tokens.append(part)

    required: List[str] = []
    optional: List[str] = []
    excluded: List[str] = []

    use_or = False
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        upper = tok.upper()
        if upper == 'OR':
            use_or = True
            i += 1
            continue
        if tok.startswith('-') and len(tok) > 1:
            excluded.append(tok[1:])
        else:
            if use_or:
                optional.append(tok)
            else:
                required.append(tok)
        use_or = False
        i += 1

    # Normalizar e remover stopwords/termos muito curtos (<=2)
    phrases = tuple(p for p in phrases if p)
    def keep_token(t: str) -> bool:
        tn = normalize_text(t)
        return bool(tn) and (len(tn) > 2) and (tn not in STOPWORDS_PT)
    required = tuple(t for t in required if keep_token(t))
    optional = tuple(t for t in optional if keep_token(t))
    excluded = tuple(t for t in excluded if keep_token(t))

    return ParsedQuery(phrases, required, optional, excluded)


def compute_match_and_highlight(text_html: str, query: ParsedQuery) -> tuple[int, str]:
    """Retorna (score, html_com_highlight).

    - Score considera: +5 por frase exata, +2 por termo obrigatório, +1 por termo opcional.
    - Exclui se algum termo proibido aparecer.
    """
    if not text_html:
        return 0, text_html

    text_norm = normalize_text(re.sub('<[^>]+>', ' ', text_html))

    # Exclusões
    for t in query.excluded_terms:
        if normalize_text(t) in text_norm:
            return 0, text_html

    score = 0
    highlights: List[Tuple[int, int]] = []

    def mark_ranges(pattern: str, weight: int) -> int:
        nonlocal highlights
        n = 0
        if not pattern:
            return 0
        patt_norm = normalize_text(pattern)
        start = 0
        while True:
            idx = text_norm.find(patt_norm, start)
            if idx == -1:
                break
            n += 1
            highlights.append((idx, idx + len(patt_norm)))
            start = idx + len(patt_norm)
        return n * weight

    for phrase in query.phrases:
        score += mark_ranges(phrase, 5)
    for term in query.required_terms:
        score += mark_ranges(term, 2)
    for term in query.optional_terms:
        score += mark_ranges(term, 1)

    # Construir HTML com <mark>, priorizando frases e evitando destacar dentro de palavras
    all_terms = list(query.phrases) + list(query.required_terms) + list(query.optional_terms)
    highlighted = text_html
    for t in sorted(all_terms, key=len, reverse=True):
        if not t:
            continue
        try:
            pattern = r"(?i)(?<![\w])" + re.escape(t) + r"(?![\w])"
            highlighted = re.sub(pattern, lambda m: f"<mark>{m.group(0)}</mark>", highlighted)
        except re.error:
            continue

    return score, highlighted


