"""
Held-out robustness suite.

IMPORTANT AND DELIBERATE LIMITATION: I wrote both the system and these
cases, so this is not a true held-out set. It measures whether the system
generalises beyond the exact strings it was tuned on, which is worth
knowing, but it cannot measure what I failed to imagine.

The genuinely independent evidence in this project is the user's own
adversarial session, which found four routing bugs my 22-case suite could
not have caught. Those became E23 to E40. This file is a weaker,
cheaper approximation of that, run BEFORE tuning rather than after.

Rule: cases here are never used to tune. If one fails and the fix is
correct, it moves to eval_set.csv as a regression test and a new unseen
case replaces it.
"""
import sys, csv; sys.path.insert(0, "..")
from collections import defaultdict
from app.corpus.build import load, approved_urls, SCHEME_IDS
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.scheme_resolver import SchemeResolver
from app.pipeline import Pipeline
from app import coverage as cov_mod

chunks, gaps = load("../data/ground_truth.csv")
pipe = Pipeline(SchemeResolver("../data/scheme_aliases.csv"),
                HybridRetriever(chunks, embedder=None), approved_urls(chunks),
                coverage=cov_mod.build(chunks, gaps, SCHEME_IDS))

rows = list(csv.DictReader(open("../data/holdout_set.csv", encoding="utf-8")))
by = defaultdict(lambda: [0, 0])
fails = []

for r in rows:
    out = pipe.answer(r["question"], r["selected_scheme"] or None)
    got = out.query_class.value
    ok = got == r["expected_class"]
    by[r["suite"]][1] += 1
    by[r["suite"]][0] += ok
    if not ok:
        fails.append((r["holdout_id"], r["question"], r["expected_class"], got, r["note"]))

total = sum(v[1] for v in by.values())
passed = sum(v[0] for v in by.values())

print("--- held-out robustness by suite ---")
for suite, (ok, n) in sorted(by.items()):
    print(f"  {suite:20s} {ok}/{n}")
print(f"\n  UNSEEN PARAPHRASE ROBUSTNESS: {passed}/{total} ({100*passed/total:.0f}%)")
if fails:
    print("\n--- failures (do not tune against these; fix, then promote to eval_set) ---")
    for f in fails:
        print(f"  {f[0]}  expected {f[2]:12s} got {f[3]:12s} | {f[1]}")
        print(f"        {f[4]}")
