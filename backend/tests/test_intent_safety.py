"""
The classifier must never see a message the guards would block.

This is the test that protects D008. If intent classification ever moves
ahead of the PII guard, a PAN would be sent to a third-party API to work
out what the user meant, which is exactly the failure the guard exists to
prevent. A spy classifier records everything handed to it.
"""
import sys; sys.path.insert(0, "..")
from app.corpus.build import load, approved_urls
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.scheme_resolver import SchemeResolver
from app.pipeline import Pipeline
from app.schemas import QueryClass

seen: list[str] = []
def spy(q: str):
    seen.append(q)
    return "min_sip"

chunks, _ = load("../data/ground_truth.csv")
p = Pipeline(SchemeResolver("../data/scheme_aliases.csv"),
             HybridRetriever(chunks, embedder=None),
             approved_urls(chunks), classifier=spy)

BLOCKED = [
    ("My PAN is ABCDE1234F, what is the minimum SIP?", QueryClass.PII),
    ("aadhaar 1234 5678 9012 minimum sip please",      QueryClass.PII),
    ("email me at omkar@example.com about the SIP",    QueryClass.PII),
    ("call me on 9876543210 about minimum sip",        QueryClass.PII),
    ("Should I buy this fund?",                        QueryClass.ADVICE),
    ("Which fund is best?",                            QueryClass.ADVICE),
]

fails = []
for q, expected in BLOCKED:
    seen.clear()
    r = p.answer(q, "SCH-02")
    if r.query_class != expected:
        fails.append(f"routing: {q!r} -> {r.query_class.value}, expected {expected.value}")
    if seen:
        fails.append(f"LEAK: classifier received a blocked message for {q!r}")

# And confirm the classifier IS reachable for safe, unmatched questions,
# otherwise this test would pass trivially.
seen.clear()
p.answer("is there some sort of holding restriction thing here", "SCH-02")
reachable = len(seen) > 0

print(f"{'PASS' if not fails else 'FAIL'}  No blocked message reaches the classifier "
      f"({len(BLOCKED)} cases)")
for f in fails:
    print("      " + f)
print(f"{'PASS' if reachable else 'FAIL'}  Classifier is reachable for safe unmatched queries")
print(f"\n{len(fails) + (0 if reachable else 1)} failures")
