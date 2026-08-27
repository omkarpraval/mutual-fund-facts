"""
Orchestrator.

Stage order (D008, revised by D042):

    PII guard                first, always, before any logging or API call
    deterministic topic      local, free, no network
    advice guard             topic-aware, so "can I" can be judged properly
    scheme resolution        aliases, then selector, then ask
    LLM topic (fallback)     only if deterministic found nothing
    retrieval
    citation validation

Deterministic topic detection moved ahead of the advice guard so the guard
can tell a permission question with a factual target ("Can I redeem after
3 years?") from one without ("Can I invest in this fund?"). It is local,
so nothing leaves the process before the guards have run. The LLM
classifier still sits after both guards.
"""
from dataclasses import dataclass, field
from app.guards import pii, advice
from app.retrieval.normaliser import topic_of
from app.retrieval.intent import resolve_topic
from app.schemas import QueryClass
from app import prompt, citation, feasibility, mixed, coverage as cov_mod


@dataclass
class Response:
    query_class: QueryClass
    message: str
    citations: list = field(default_factory=list)
    scheme: str | None = None
    evidence_used: int = 0
    hits: list = field(default_factory=list)
    conflict: str | None = None        # selector said X, question said Y
    known_gap: bool = False
    candidates: list = field(default_factory=list)   # ambiguous scheme options
    partial_refusal: str | None = None               # mixed factual + advice
    available: list = field(default_factory=list)
    debug: dict = field(default_factory=dict)


class Pipeline:
    def __init__(self, resolver, retriever, approved_urls, generator=None,
                 classifier=None, coverage=None):
        self.resolver, self.retriever = resolver, retriever
        self.approved_urls, self.generator = approved_urls, generator
        self.classifier, self.coverage = classifier, coverage

    def answer(self, question: str, selected_scheme_id: str | None = None) -> Response:
        # 1. PII. Nothing logged or sent anywhere before this returns.
        if kinds := pii.scan(question):
            return Response(QueryClass.PII, pii.MESSAGE, debug={"pii_kinds": kinds})

        # 2. Local topic detection. No network, so guard ordering holds.
        topic = topic_of(question)

        # 3. Advice. Before refusing outright, check whether the question
        #    mixes a separable factual clause with an advisory one.
        partial = None
        if kind := advice.detect(question, topic):
            fact_clause, adv_kind = mixed.analyse(question, topic_of, advice.detect)
            if fact_clause and adv_kind:
                question, topic = fact_clause[0], fact_clause[1]
                partial = advice.refusal_message(adv_kind)
            else:
                return Response(QueryClass.ADVICE, advice.refusal_message(kind),
                                debug={"refusal_kind": kind.value})

        # 4. Scheme. An explicit mention always overrides the selector, and
        #    a mismatch is surfaced rather than silently resolved.
        m = self.resolver.resolve(question, selected_scheme_id)
        conflict = None
        if (m.matched_on == "question_alias" and selected_scheme_id
                and m.scheme_id != selected_scheme_id):
            conflict = self.resolver.canonical(selected_scheme_id)

        # 5. LLM topic only if local found nothing. After both guards.
        how = "lookup"
        if topic is None:
            topic, how = resolve_topic(question, self.classifier)

        if m.matched_on == "ambiguous":
            return Response(QueryClass.NEEDS_SCHEME,
                            "I have several SBI schemes in scope. Which one do you mean?",
                            candidates=m.candidates or [])

        if m.scheme_id is None and topic not in ("capital_gains_statement",):
            return Response(QueryClass.NEEDS_SCHEME, prompt.NEEDS_SCHEME)

        # 5b. Recognised scheme, unrecognised topic. Not a retrieval
        #     failure: the question falls outside the FAQ taxonomy.
        if topic is None and self.coverage:
            avail = cov_mod.available_labels(self.coverage, m.scheme_id)
            return Response(
                QueryClass.OUT_OF_SCOPE,
                f"I answer a defined set of factual questions, and this one "
                f"isn't among them for {m.canonical_name}.",
                scheme=m.canonical_name, conflict=conflict,
                available=avail, partial_refusal=partial)

        # 6. Known gap: we understood the question and do not have it verified.
        if self.coverage and cov_mod.is_known_gap(self.coverage, m.scheme_id, topic):
            avail = cov_mod.available_labels(self.coverage, m.scheme_id)
            return Response(
                QueryClass.OUT_OF_SCOPE,
                f"I have verified information for {m.canonical_name}, but "
                f"{cov_mod.label(topic).lower()} isn't in the official sources "
                f"indexed for it yet.",
                scheme=m.canonical_name, conflict=conflict,
                known_gap=True, available=avail, partial_refusal=partial)

        # 7. Retrieval.
        drop = [m.matched_text] if m.matched_on == "question_alias" and m.matched_text else []
        hits = self.retriever.search(question, scheme_id=m.scheme_id,
                                     topic=topic, drop_terms=drop)
        if not hits:
            avail = cov_mod.available_labels(self.coverage, m.scheme_id) if self.coverage else []
            return Response(QueryClass.OUT_OF_SCOPE, prompt.NO_EVIDENCE,
                            scheme=m.canonical_name, conflict=conflict,
                            available=avail, partial_refusal=partial)

        cits = citation.build([h.chunk for h in hits])
        if bad := citation.validate(cits, self.approved_urls):
            return Response(QueryClass.OUT_OF_SCOPE, prompt.NO_EVIDENCE,
                            debug={"unapproved_citations": bad})

        # 8. Feasibility: a stated amount turns a lookup into a check.
        lead = None
        if topic == "min_sip":
            amt = feasibility.parse_amount(question)
            lead = feasibility.assess_sip(m.canonical_name, amt,
                                          feasibility.parse_frequency(question))

        text = (self.generator(prompt.SYSTEM_PROMPT, prompt.build_context(hits), question)
                if self.generator else "[generation pending]")
        return Response(QueryClass.FACTUAL, text, citations=cits,
                        scheme=m.canonical_name, evidence_used=len(hits), hits=hits,
                        conflict=conflict, partial_refusal=partial,
                        debug={"matched_on": m.matched_on, "topic": topic,
                               "topic_via": how, "feasibility": lead})
