import sys; sys.path.insert(0, "..")
from fixture_corpus import build
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.scheme_resolver import SchemeResolver
from app.pipeline import Pipeline
from app.schemas import QueryClass

chunks = build()
p = Pipeline(SchemeResolver("../data/scheme_aliases.csv"),
             HybridRetriever(chunks, embedder=None),
             {c.source_url for c in chunks})

cases = [
    ("My PAN is ABCDE1234F, what is the exit load?", None, QueryClass.PII),
    ("Should I buy SBI Flexicap Fund?",              None, QueryClass.ADVICE),
    ("Which fund will give the best returns?",       None, QueryClass.ADVICE),
    ("What is the minimum SIP?",                     None, QueryClass.NEEDS_SCHEME),
    ("What is the exit load?",                   "SCH-02", QueryClass.FACTUAL),
    ("SBI Magnum Multicap Fund exit load?",          None, QueryClass.FACTUAL),
    ("SBI Bluechip Fund exit load?",                 None, QueryClass.OUT_OF_SCOPE),
    ("Does SBI Long Term Equity Fund have a lock in?", None, QueryClass.FACTUAL),
    ("Who is the fund manager?",                 "SCH-02", QueryClass.OUT_OF_SCOPE),
]

fails = []
print(f"{'EXPECTED':<16}{'GOT':<16}QUERY")
for q, sel, exp in cases:
    r = p.answer(q, sel)
    ok = r.query_class == exp
    if not ok: fails.append((q, exp.value, r.query_class.value))
    print(f"{exp.value:<16}{r.query_class.value:<16}{'ok  ' if ok else 'FAIL'} {q[:46]}")
print(f"\n{len(fails)} failures")
for f in fails: print("   ", f)
