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
from app.graph.workflow import build_graph


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
        # Compile LangGraph state workflow
        self.graph = build_graph(
            resolver=resolver,
            retriever=retriever,
            approved_urls=approved_urls,
            generator=generator,
            classifier=classifier,
            coverage=coverage
        )

    def answer(self, question: str, selected_scheme_id: str | None = None) -> Response:
        initial_state = {
            "question": question,
            "selected_scheme_id": selected_scheme_id
        }
        final_state = self.graph.invoke(initial_state)

        return Response(
            query_class=final_state.get("query_class", QueryClass.OUT_OF_SCOPE),
            message=final_state.get("message", prompt.NO_EVIDENCE),
            citations=final_state.get("citations", []),
            scheme=final_state.get("canonical_name"),
            evidence_used=len(final_state.get("hits", [])),
            hits=final_state.get("hits", []),
            conflict=final_state.get("conflict"),
            known_gap=final_state.get("known_gap", False),
            candidates=final_state.get("candidates", []),
            partial_refusal=final_state.get("partial_refusal"),
            available=final_state.get("available_labels", []),
            debug=final_state.get("debug", {})
        )
