"""
Mixed-intent handling (D045).

"What is the TER, and should I invest?" contains two questions. Answering
both would give advice. Refusing both withholds a fact we have verified
and cited. Neither is right.

We split on coordinating conjunctions, classify each clause separately,
answer the factual clauses, and decline the advisory ones in the same
response.

The safety asymmetry from D009 survives intact: a clause is only answered
if it independently passes the advice guard AND resolves to a factual
topic. Anything ambiguous stays refused. Splitting never turns an
advisory clause into an answerable one; it only stops an advisory clause
from suppressing a separable factual one.
"""
import re

SPLIT = re.compile(r"\s*(?:,\s*(?:and|or|but)\b|\band\b|\bor\b|\bbut\b|;)\s*", re.I)
MIN_CLAUSE = 8


def split_clauses(question: str) -> list[str]:
    parts = [p.strip(" ?.,") for p in SPLIT.split(question) if p and p.strip(" ?.,")]
    return [p for p in parts if len(p) >= MIN_CLAUSE] or [question]


def analyse(question: str, detect_topic, advice_detect):
    """
    Returns (factual_clause, advice_kind) when the question genuinely
    mixes both, otherwise (None, None) and the caller handles it whole.
    """
    clauses = split_clauses(question)
    if len(clauses) < 2:
        return None, None

    factual, advisory = None, None
    for c in clauses:
        topic = detect_topic(c)
        kind = advice_detect(c, topic)
        if kind and advisory is None:
            advisory = kind
        elif not kind and topic and factual is None:
            factual = (c, topic)

    return (factual, advisory) if (factual and advisory) else (None, None)
