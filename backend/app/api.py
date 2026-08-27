"""FastAPI surface. Thin: all behaviour lives in the pipeline."""
import os
from pathlib import Path as _P

# Load .env before anything reads os.environ. No dependency needed.
_envf = _P(__file__).resolve().parent.parent / ".env"
if _envf.exists():
    for _line in _envf.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path

from app.corpus.build import load, approved_urls, SCHEME_IDS
from app import coverage as cov_mod
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.scheme_resolver import SchemeResolver
from app.pipeline import Pipeline
from app.generator import get_generator, extractive
from app.schemas import QueryClass
from app import prompt

DATA = Path(__file__).resolve().parent.parent / "data"

chunks, gaps = load(DATA / "ground_truth.csv")
resolver = SchemeResolver(DATA / "scheme_aliases.csv")
retriever = HybridRetriever(chunks, embedder=None)
_gen = get_generator()


def _generate(system, context, question, hits=None):
    return _gen(system, context, question, hits) if _gen else extractive(hits or [], question)


COVERAGE = cov_mod.build(chunks, gaps, SCHEME_IDS)
pipeline = Pipeline(resolver, retriever, approved_urls(chunks), coverage=COVERAGE)

app = FastAPI(title="Mutual Fund Facts Assistant", version="0.7.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"],
                   allow_methods=["POST", "GET"], allow_headers=["*"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    scheme_id: str | None = None


class Citation(BaseModel):
    title: str
    url: str
    organization: str
    last_updated: str | None
    fact_as_of: str | None = None
    source_dated: str | None = None
    retrieved_at: str | None = None


class ChatResponse(BaseModel):
    state: str
    message: str
    scheme: str | None = None
    citations: list[Citation] = []
    stale: bool = False
    conflict: str | None = None
    known_gap: bool = False
    available: list[str] = []
    candidates: list[dict] = []
    partial_refusal: str | None = None
    verification: str = "verified"
    condition: str | None = None
    fact_label: str | None = None
    fact_value: str | None = None


@app.get("/api/health")
def health():
    return {"status": "ok", "version": app.version,
            "chunks": len(chunks), "known_gaps": len(gaps),
            "schemes": [s["canonical_name"] for s in resolver.schemes.values()],
            "llm": "configured" if _gen else "extractive fallback"}


@app.get("/api/coverage")
def api_coverage():
    """Returns columns, rows, and chips for the Certainty Ledger and quick-fact chips."""
    return cov_mod.full_coverage(COVERAGE, resolver.schemes)


@app.get("/api/schemes")
def schemes():
    return [{"id": k, "name": v["canonical_name"], "former_name": v["former_name"]}
            for k, v in resolver.schemes.items()]


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    q = req.question.strip()
    if len(q) > 400:
        return ChatResponse(state="too_long",
                            message="That question is longer than I can process. "
                                    "Try asking about one fact at a time.")

    r = pipeline.answer(q, req.scheme_id)

    if r.query_class == QueryClass.FACTUAL:
        hits = r.hits
        text = prompt.cap_sentences(
            _generate(prompt.SYSTEM_PROMPT, prompt.build_context(hits), q, hits))
        # A stated amount turns a lookup into a factual feasibility check.
        if lead := r.debug.get("feasibility"):
            text = prompt.cap_sentences(lead + " " + text, limit=3)

        # Strip duplicated scheme prefix if present (Section P0)
        if r.scheme:
            for sep in [" - ", ": "]:
                prefix = f"{r.scheme}{sep}"
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()

        # Verification state and condition reasoning
        topic = r.debug.get("topic", "")
        if topic == "riskometer" or (hits and hits[0].chunk.topic == "riskometer"):
            verification = "conditional"
            condition = "Taken from the KIM, which is a snapshot. The monthly factsheet is the authoritative source for this value."
        else:
            verification = "verified"
            condition = None

        fact_label = None
        fact_value = None
        if hits and hits[0].chunk.fact_label and hits[0].chunk.fact_value:
            if not (topic == "min_sip" and "Frequency-dependent" in hits[0].chunk.text):
                fact_label = hits[0].chunk.fact_label
                fact_value = hits[0].chunk.fact_value

        return ChatResponse(
            state="answer", message=text, scheme=r.scheme,
            citations=[Citation(**c.__dict__) for c in r.citations],
            stale="may not be the current value" in text,
            conflict=r.conflict, partial_refusal=r.partial_refusal,
            verification=verification, condition=condition,
            fact_label=fact_label, fact_value=fact_value)

    state = {QueryClass.ADVICE: "refusal", QueryClass.PII: "pii",
             QueryClass.NEEDS_SCHEME: "needs_scheme",
             QueryClass.OUT_OF_SCOPE: "known_gap" if r.known_gap else "no_evidence"}[r.query_class]

    candidates = r.candidates
    if state == "needs_scheme" and not candidates:
        candidates = [{"id": k, "name": v["canonical_name"]} for k, v in resolver.schemes.items()]

    return ChatResponse(state=state, message=r.message, scheme=r.scheme,
                        conflict=r.conflict, known_gap=r.known_gap,
                        available=r.available, candidates=candidates,
                        partial_refusal=r.partial_refusal)
