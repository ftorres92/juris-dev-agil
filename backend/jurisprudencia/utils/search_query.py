from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, Optional, Set, Tuple


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

# Stopwords PT fornecidas + complementos para evitar matches irrelevantes.
STOPWORDS_BASE = {
    'de','a','o','que','e','do','da','em','um','para','é','com','não','uma','os','no','se','na','por','mais','as',
    'dos','como','mas','foi','ao','ele','das','tem','à','seu','sua','ou','ser','quando','muito','há','nos','já',
    'está','eu','também','só','pelo','pela','até','isso','ela','entre','era','depois','sem','mesmo','aos','ter',
    'seus','quem','nas','me','esse','eles','estão','você','tinha','foram','essa','num','nem','suas','meu','às',
    'minha','têm','numa','pelos','elas','havia','seja','qual','será','nós','tenho','lhe','deles','essas','esses',
    'pelas','este','fosse','dele','tu','te','vocês','vos','lhes','meus','minhas','teu','tua','teus','tuas',
    'nosso','nossa','nossos','nossas','dela','delas','esta','estes','estas','aquele','aquela','aqueles','aquelas',
    'isto','aquilo','estou','estamos','estão','estive',
}

STOPWORDS_EXTRA = {
    'às','aos','as','os','uns','umas','d','pra','pro','nuns','numas','sob','sobre','antes','contra','desde',
    'trás','onde','quais','menos','muita','muitos','muitas','num','numa','ela','ele','elas','eles','sua','seu',
    'suas','seus','pra','pro','entre',
}

STOPWORDS_PT = STOPWORDS_BASE | STOPWORDS_EXTRA

SHORT_TOKEN_WHITELIST = {
    'tj', 'tjdf', 'tjsp', 'tjmg', 'tjrs', 'tjpr', 'tjba', 'tjce', 'tjgo', 'tjpa', 'tjsc', 'tjpe',
    'stf', 'stj', 'tst', 'trt', 'trf', 'cnj', 'clt', 'oj',
}

PHRASE_WEIGHT = 5
REQUIRED_WEIGHT = 2
OPTIONAL_WEIGHT = 1

_TAG_RE = re.compile('<[^>]+>')


@dataclass(frozen=True)
class NormalizedQuery:
    phrases: Tuple[str, ...]
    required_terms: Tuple[str, ...]
    optional_terms: Tuple[str, ...]
    excluded_terms: Tuple[str, ...]


def _normalize_sequence(values: Iterable[str]) -> Tuple[str, ...]:
    return tuple(filter(None, (normalize_text(value) for value in values)))


@lru_cache(maxsize=256)
def _normalized_query(query: 'ParsedQuery') -> NormalizedQuery:
    return NormalizedQuery(
        phrases=_normalize_sequence(query.phrases),
        required_terms=_normalize_sequence(query.required_terms),
        optional_terms=_normalize_sequence(query.optional_terms),
        excluded_terms=_normalize_sequence(query.excluded_terms),
    )


@lru_cache(maxsize=512)
def _boundary_regex(token: str) -> re.Pattern[str]:
    if not token:
        return re.compile(r'(?!)')
    return re.compile(rf'(?<!\w){re.escape(token)}(?!\w)')


OR_KEYWORDS = {'OR', 'OU'}

DENSITY_WEIGHT = 3.0
LEAD_BONUS_BASE = 4.0
LEAD_BONUS_DECAY = 80.0


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
        if upper in OR_KEYWORDS:
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
        if not tn or tn in STOPWORDS_PT:
            return False
        if len(tn) > 2:
            return True
        if any(ch.isdigit() for ch in tn):
            return True
        if tn in SHORT_TOKEN_WHITELIST:
            return True
        # Mantém siglas curtas digitadas em caixa alta (ex.: "TJ")
        if t.isupper() and len(tn) >= 2:
            return True
        return False
    required = tuple(t for t in required if keep_token(t))
    optional = tuple(t for t in optional if keep_token(t))
    excluded = tuple(t for t in excluded if keep_token(t))

    return ParsedQuery(phrases, required, optional, excluded)


def _token_stats(text_norm: str, token: str) -> Tuple[int, Optional[int]]:
    if not token:
        return 0, None
    pattern = _boundary_regex(token)
    count = 0
    first_pos: Optional[int] = None
    for match in pattern.finditer(text_norm):
        count += 1
        if first_pos is None:
            first_pos = match.start()
    return count, first_pos


def _has_token(words: Set[str], text_norm: str, token: str) -> bool:
    if not token:
        return False
    if ' ' in token:
        count, _ = _token_stats(text_norm, token)
        return count > 0
    return token in words


def _find_tag_ranges(text_html: str) -> List[Tuple[int, int]]:
    ranges: List[Tuple[int, int]] = []
    cursor = 0
    while True:
        start = text_html.find('<', cursor)
        if start == -1:
            break
        end = text_html.find('>', start + 1)
        if end == -1:
            break
        ranges.append((start, end + 1))
        cursor = end + 1
    return ranges


def _ranges_overlap(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def _is_inside_tag(ranges: List[Tuple[int, int]], start: int, end: int) -> bool:
    for a, b in ranges:
        if start >= a and end <= b:
            return True
    return False


def accent_agnostic_pattern(token: str) -> str:
    subs = {
        'a': '[aáàâãä]', 'e': '[eéèêë]', 'i': '[iíìîï]', 'o': '[oóòôõö]', 'u': '[uúùûü]',
        'c': '[cç]'
    }
    out = []
    for ch in token:
        if ch.isspace():
            out.append(r'\s+')
            continue
        low = ch.lower()
        out.append(subs.get(low, re.escape(ch)))
    return ''.join(out)


def _compile_highlight_regex(token: str) -> re.Pattern[str] | None:
    try:
        return re.compile(rf'(?i)(?<!\w){accent_agnostic_pattern(token)}(?!\w)')
    except re.error:
        return None


def _apply_highlight(text_html: str, terms: Iterable[str]) -> str:
    unique_terms = [t for t in dict.fromkeys(term for term in terms if term)]
    if not unique_terms:
        return text_html

    tag_ranges = _find_tag_ranges(text_html)
    highlight_ranges: List[Tuple[int, int]] = []

    for term in sorted(unique_terms, key=len, reverse=True):
        regex = _compile_highlight_regex(term)
        if not regex:
            continue
        for match in regex.finditer(text_html):
            start, end = match.span()
            if _is_inside_tag(tag_ranges, start, end):
                continue
            if any(_ranges_overlap((start, end), existing) for existing in highlight_ranges):
                continue
            highlight_ranges.append((start, end))

    if not highlight_ranges:
        return text_html

    highlight_ranges.sort()
    pieces: List[str] = []
    cursor = 0
    for start, end in highlight_ranges:
        pieces.append(text_html[cursor:start])
        pieces.append('<mark>')
        pieces.append(text_html[start:end])
        pieces.append('</mark>')
        cursor = end
    pieces.append(text_html[cursor:])
    return ''.join(pieces)


def compute_match_and_highlight(
    text_html: str,
    query: ParsedQuery,
    *,
    weight_multiplier: float = 1.0,
    enforce_filters: bool = True,
    highlight: bool = True,
) -> tuple[int, str]:
    """Calcula score e destaca termos encontrados em ``text_html``."""

    if not text_html:
        return 0, text_html

    text_plain = _TAG_RE.sub(' ', text_html)
    text_norm = normalize_text(text_plain)
    if not text_norm:
        return 0, text_html

    norm_query = _normalized_query(query)
    words_set = set(text_norm.split())

    # Termos proibidos eliminam o documento.
    for token in norm_query.excluded_terms:
        if _has_token(words_set, text_norm, token):
            return 0, text_html

    raw_score = 0
    missing_required = False
    missing_phrase = False
    matched_terms: Set[str] = set()
    first_hit_positions: List[int] = []

    for original, normalized in zip(query.phrases, norm_query.phrases):
        count, first_pos = _token_stats(text_norm, normalized)
        if count:
            raw_score += count * PHRASE_WEIGHT
            matched_terms.add(original)
            if first_pos is not None:
                first_hit_positions.append(first_pos)
        else:
            missing_phrase = True

    for original, normalized in zip(query.required_terms, norm_query.required_terms):
        count, first_pos = _token_stats(text_norm, normalized)
        if count:
            raw_score += count * REQUIRED_WEIGHT
            matched_terms.add(original)
            if first_pos is not None:
                first_hit_positions.append(first_pos)
        else:
            missing_required = True

    for original, normalized in zip(query.optional_terms, norm_query.optional_terms):
        count, first_pos = _token_stats(text_norm, normalized)
        if count:
            raw_score += count * OPTIONAL_WEIGHT
            matched_terms.add(original)
            if first_pos is not None:
                first_hit_positions.append(first_pos)

    if enforce_filters:
        if norm_query.phrases and missing_phrase:
            return 0, text_html
        if norm_query.required_terms and missing_required:
            return 0, text_html

    score_value = float(raw_score) * weight_multiplier

    if raw_score > 0:
        word_count = max(1, len(text_norm.split()))
        density_bonus = (raw_score / word_count) * DENSITY_WEIGHT * weight_multiplier
        score_value += density_bonus

        if first_hit_positions:
            best_position = min(first_hit_positions)
            lead_bonus = max(0.0, LEAD_BONUS_BASE - (best_position / LEAD_BONUS_DECAY)) * weight_multiplier
            score_value += lead_bonus

    score = int(round(score_value))
    highlighted = _apply_highlight(text_html, matched_terms) if highlight else text_html
    return score, highlighted
