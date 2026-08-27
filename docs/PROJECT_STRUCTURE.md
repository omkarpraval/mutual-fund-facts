# Project structure

```
mf-facts-assistant/
├── README.md                       project overview, setup, scope, known limits
│
├── docs/
│   ├── 01_product_discovery.md     problem, user, JTBD, hypothesis, assumptions, risks
│   ├── 02_source_research.md       source tiers, freshness policy, conflict policy
│   ├── 03_scope.md                 AMC and scheme selection with scoring
│   ├── decision_log.md             37 decisions with alternatives and trade-offs
│   ├── collection_checklist.md     manual collection procedure and quality gate
│   ├── evaluation_report.txt       latest harness run
│   └── PROJECT_STRUCTURE.md        this file
│
├── data/
│   ├── sources.csv                 26 source URLs with tier and metadata
│   ├── ground_truth.csv            46 facts, four verification states
│   ├── scheme_aliases.csv          canonical and former names per scheme
│   └── eval_set.csv                22 evaluation questions
│
├── backend/
│   ├── run.sh
│   ├── data/                       runtime copy of the CSVs above
│   ├── app/
│   │   ├── api.py                  FastAPI: /api/chat, /api/health, /api/schemes
│   │   ├── pipeline.py             fixed-order orchestrator
│   │   ├── schemas.py              chunk and fact types, staleness windows
│   │   ├── prompt.py               system prompt, ten generation rules
│   │   ├── generator.py            Gemini / Groq / extractive fallback
│   │   ├── embedder.py             local sentence-transformers, optional
│   │   ├── freshness.py            staleness annotation for dynamic facts
│   │   ├── citation.py             citation building and approval check
│   │   ├── guards/
│   │   │   ├── pii.py              runs first, never echoes matched values
│   │   │   └── advice.py           five-branch refusal taxonomy
│   │   ├── retrieval/
│   │   │   ├── scheme_resolver.py  alias-first scheme resolution
│   │   │   ├── normaliser.py       question to FAQ topic
│   │   │   └── hybrid.py           coverage gate, BM25 + dense, tier ordering
│   │   └── corpus/
│   │       ├── build.py            verification state gates indexing
│   │       └── chunker.py          section-aware chunking, label/value audit
│   └── tests/
│       ├── run_eval.py             scored against ground truth
│       ├── test_guards.py          PII and advice detection
│       ├── test_resolution.py      alias resolution, topic normalisation
│       ├── test_pipeline.py        chunking, retrieval, citation, freshness
│       ├── test_end_to_end.py      routing across all response classes
│       └── fixture_corpus.py       placeholder corpus for offline testing
│
└── frontend/
    ├── app/
    │   ├── page.tsx                scheme selector, input, state routing
    │   ├── layout.tsx
    │   └── globals.css             design tokens
    ├── components/
    │   ├── Provenance.tsx          the signature element: source + as-of date
    │   └── Cards.tsx               answer, refusal, PII, no-evidence, error, empty, loading
    └── lib/api.ts                  typed client
```

## Reading order for a reviewer

1. `README.md` for what it does and what it deliberately will not do
2. `docs/01_product_discovery.md` for the problem and the reasoning
3. `docs/decision_log.md` for how each decision was actually made
4. `data/ground_truth.csv` for what the system knows and what it refuses to claim
5. `docs/evaluation_report.txt` for measured behaviour

## Still open

- Large Cap minimum SIP and investment objective, not yet extracted
- ELSS minimum application amount, SID table extraction was malformed
- Groww capital-gains flow, official article internally inconsistent
- Current factsheet, latest located is March 2026
- PRD, sample_qa.md, demo recording
