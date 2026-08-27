import sys; sys.path.insert(0, "..")
from datetime import date
from fixture_corpus import build
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.scheme_resolver import SchemeResolver
from app.retrieval.normaliser import detect_topic
from app.corpus.chunker import audit_labels
from app.schemas import FactType
from app import freshness, citation

chunks = build()
R = SchemeResolver("../data/scheme_aliases.csv")
retr = HybridRetriever(chunks, embedder=None)   # BM25 only offline
APPROVED = {c.source_url for c in chunks}
fails = []

# 1. chunker preserved label/value pairs (R7 gate)
probs = audit_labels(chunks)
print(f"{'PASS' if not probs else 'FAIL'}  Chunker label/value integrity ({len(chunks)} chunks)")
fails += probs

# 2. wrong-scheme leakage (R3) - ELSS lock-in must not surface for Flexicap
m = R.resolve("lock in period", "SCH-02")
hits = retr.search("lock in period", scheme_id=m.scheme_id, top_k=4)
leaked = [h for h in hits if h.chunk.scheme_id == "SCH-03"]
print(f"{'PASS' if not leaked else 'FAIL'}  No wrong-scheme leakage")
if leaked: fails.append(f"ELSS chunk leaked into SCH-02 query")

# 3. former-name query routes correctly and retrieves
m = R.resolve("SBI Magnum Multicap Fund exit load")
hits = retr.search("exit load", scheme_id=m.scheme_id, topic=detect_topic("exit load"))
ok = m.scheme_id == "SCH-02" and hits and "Exit Load" in hits[0].chunk.text
print(f"{'PASS' if ok else 'FAIL'}  Former-name query retrieves correct chunk")
if not ok: fails.append("former-name retrieval failed")

# 4. tier-2 chunk stays eligible under a scheme filter
# Mirror real pipeline usage: the topic is always resolved before search.
q = "total expense ratio disclosure"
hits = retr.search(q, scheme_id="SCH-02", topic=detect_topic(q))
ok = any(h.chunk.tier == 2 for h in hits)
print(f"{'PASS' if ok else 'FAIL'}  Tier-2 regulatory chunk eligible under scheme filter")
if not ok: fails.append("tier-2 chunk filtered out incorrectly")

# 5. relevance floor -> no-evidence rather than a guess
q = "who is the fund manager and what is the AUM"
hits = retr.search(q, scheme_id="SCH-02", topic=detect_topic(q))
print(f"{'PASS' if not hits else 'FAIL'}  Out-of-corpus query returns no evidence")
if hits: fails.append(f"out-of-corpus returned {len(hits)} hits")

# 6. citation is specific, never a homepage
cits = citation.build([hits[0].chunk] if hits else [chunks[0]])
bad = citation.validate(cits, APPROVED)
ok = cits and not bad and cits[0].url.count("/") > 3
print(f"{'PASS' if ok else 'FAIL'}  Citation resolves to an approved specific source")
if not ok: fails.append(f"citation problem: {bad or cits}")

# 7. freshness: fresh vs stale TER
fresh = freshness.annotate("The TER is X%.", FactType.DYNAMIC_DAILY,
                           "2026-08-26", today=date(2026, 8, 28))
stale = freshness.annotate("The TER is X%.", FactType.DYNAMIC_DAILY,
                           "2026-08-26", today=date(2026, 9, 20))
ok = "may not be the current value" not in fresh and "may not be the current value" in stale
print(f"{'PASS' if ok else 'FAIL'}  Staleness threshold fires at the right time")
if not ok: fails.append("freshness thresholds wrong")

print(f"\n{len(fails)} failures")
for f in fails: print("   ", f)
