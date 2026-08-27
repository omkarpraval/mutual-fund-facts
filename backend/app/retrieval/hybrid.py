"""
Hybrid retrieval (D012): BM25 keyword + dense semantic, fused.

Most target facts are exact strings: Rs. 500, 1%, 30 days, 3 years,
Nifty 500 TRI. Dense embeddings are mediocre at exact tokens, which is
what this corpus is full of. BM25 covers that; dense covers paraphrase.

Metadata filtering by scheme runs BEFORE scoring, so a wrong-scheme
chunk can never win on similarity alone (R3).
"""
import re
from dataclasses import dataclass
from rank_bm25 import BM25Okapi
from app.schemas import Chunk
from app.retrieval.normaliser import TOPIC_SYNONYMS


def expand(chunk: Chunk) -> str:
    """
    Index-time vocabulary expansion. The corpus speaks in document terms
    ("TER", "Riskometer"); users speak in plain terms ("expense ratio",
    "how risky"). Without this the coverage gate rejects correct chunks
    for using the official word.
    """
    key = (chunk.topic or "").split(";")[0]
    for topic, phrases in TOPIC_SYNONYMS.items():
        if key.startswith(topic) or topic.startswith(key):
            return chunk.text + " " + " ".join(phrases)
    return chunk.text

# Two independent gates, and they do different jobs.
#
# COVERAGE_FLOOR is the important one. Min-max normalisation always hands
# the best candidate a 1.0 no matter how irrelevant it is, so a normalised
# score can never express "nothing here is relevant". A lexical coverage
# gate can: we require a share of the query's content words to actually
# appear in the chunk before it is eligible at all.
COVERAGE_FLOOR = 0.40

# When the question maps to no known FAQ topic, demand much stronger lexical
# evidence. "Who is the fund manager?" scores 0.50 purely on the generic word
# "fund" appearing in a regulatory chunk - a match on vocabulary, not on
# meaning. An unrecognised topic is the single best signal that a question
# falls outside the taxonomy, so it raises the bar rather than lowering it.
UNKNOWN_TOPIC_FLOOR = 0.65

# NOTE: a numeric relevance floor used to sit here and has been removed.
# D025 established that the coverage gate decides ELIGIBILITY and the
# normalised score only RANKS the survivors. Keeping a score floor as
# well contradicted that and silently discarded correct evidence: the
# right TER chunk normalised to 0.11, just under a 0.12 floor, so the
# answer fell back to a general regulatory chunk. Eligibility is decided
# in exactly one place.

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "of", "for", "to",
    "in", "on", "at", "and", "or", "what", "which", "who", "how", "much",
    "many", "does", "do", "did", "this", "that", "it", "its", "my", "i",
    "can", "will", "with", "from", "by", "as", "if", "there", "any",
}


@dataclass
class Scored:
    chunk: Chunk
    score: float
    bm25: float
    dense: float


def _tok(s: str) -> list[str]:
    """
    Punctuation-aware tokenisation. Splitting on whitespace alone leaves
    "[expense" and "ratio]" as tokens, which silently fails to match
    "expense ratio" - and this corpus is full of "Rs.", "(TER)", "1%".
    Percentages are kept whole because they are often the answer.
    """
    return re.findall(r"[a-z0-9]+(?:\.[0-9]+)?%?", s.lower())


def _content(s: str) -> list[str]:
    return [t for t in _tok(s) if t not in STOPWORDS]


def _coverage(query: str, text: str) -> float:
    q = _content(query)
    if not q:
        return 0.0
    have = set(_tok(text))
    return sum(1 for t in q if t in have) / len(q)


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], embedder=None, alpha: float = 0.5):
        self.chunks = chunks
        self.embedder = embedder          # None -> BM25 only (testable offline)
        self.alpha = alpha
        self._expanded = [expand(c) for c in chunks]
        self._bm25 = BM25Okapi([_tok(t) for t in self._expanded])
        self._vecs = embedder.encode([c.text for c in chunks]) if embedder else None

    @staticmethod
    def _norm(xs):
        """
        Min-max, but ties resolve UP rather than down. When one candidate
        survives the coverage gate, or several score identically, they are
        all equally good - not all equally worthless. Returning zeros here
        made the relevance floor reject the only correct chunk.
        """
        lo, hi = min(xs, default=0.0), max(xs, default=0.0)
        if hi - lo < 1e-9:
            return [1.0 if hi > 0 else 0.0] * len(xs)
        return [(x - lo) / (hi - lo) for x in xs]

    def search(self, query: str, *, scheme_id: str | None = None,
               topic: str | None = None, top_k: int = 4,
               drop_terms: list[str] | None = None) -> list[Scored]:
        # The scheme name is already handled by metadata filtering, so leaving
        # it in the query only dilutes coverage: "SBI Magnum Multicap Fund
        # exit load" scored 0.33 against the very chunk that answers it,
        # because four of its six content words name the fund, not the fact.
        for term in (drop_terms or []):
            query = re.sub(re.escape(term), " ", query, flags=re.I)

        idx = list(range(len(self.chunks)))

        # Metadata filter first (D003). Tier 2 and 3 chunks carry no scheme
        # and stay eligible, since regulatory and platform facts are shared.
        if scheme_id:
            idx = [i for i in idx if self.chunks[i].scheme_id in (scheme_id, None)]
        if topic:
            # No fallback. If the corpus holds no chunk for this topic,
            # that is a genuine gap and must surface as no-evidence.
            idx = [i for i in idx if topic in (self.chunks[i].topic or "")]
        # Coverage gate before scoring: this is what makes a genuine
        # no-evidence answer possible instead of a confident guess.
        floor = COVERAGE_FLOOR if topic else UNKNOWN_TOPIC_FLOOR
        idx = [i for i in idx if _coverage(query, self._expanded[i]) >= floor]
        if not idx:
            return []

        bm = self._bm25.get_scores(_tok(query))
        bm_f = self._norm([bm[i] for i in idx])

        if self._vecs is not None:
            qv = self.embedder.encode([query])[0]
            dn = [sum(a * b for a, b in zip(qv, self._vecs[i])) for i in idx]
            dn_f = self._norm(dn)
        else:
            dn_f = [0.0] * len(idx)

        scored = []
        for i, b, d in zip(idx, bm_f, dn_f):
            base = self.alpha * b + (1 - self.alpha) * d if self._vecs is not None else b
            scored.append(Scored(self.chunks[i], base, b, d))

        # Source hierarchy is CATEGORICAL, not a nudge. Tier 1 owns scheme
        # facts, so when a scheme is resolved, a chunk carrying that scheme's
        # own fact outranks any general regulatory chunk sharing the topic -
        # regardless of relative similarity. An additive boost failed here:
        # AMFI's longer definition of TER out-scored SBI's actual TER value
        # on raw BM25, and citing a definition instead of the figure is a
        # citation-accuracy failure even though the answer text may look fine.
        def rank(s: Scored):
            own = 1 if (scheme_id and s.chunk.scheme_id == scheme_id) else 0
            return (own, s.score)

        scored.sort(key=rank, reverse=True)
        return scored[:top_k]
