"""Evaluation harness. Scores against ground_truth.csv, never by inspection."""
import sys, csv, time; sys.path.insert(0, "..")
from collections import defaultdict
from app.corpus.build import load, approved_urls, SCHEME_IDS
from app import coverage as cov_mod
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.scheme_resolver import SchemeResolver
from app.pipeline import Pipeline
from app.schemas import QueryClass

chunks, gaps = load("../data/ground_truth.csv")
pipe = Pipeline(SchemeResolver("../data/scheme_aliases.csv"),
                HybridRetriever(chunks, embedder=None),
                approved_urls(chunks),
                coverage=cov_mod.build(chunks, gaps, SCHEME_IDS))
GT = {c.chunk_id: c for c in chunks}

rows = list(csv.DictReader(open("../data/eval_set.csv", encoding="utf-8")))
res, by_cat = [], defaultdict(lambda: [0, 0])

for r in rows:
    t0 = time.perf_counter()
    out = pipe.answer(r["question"], r["selected_scheme"] or None)
    ms = (time.perf_counter() - t0) * 1000

    class_ok = out.query_class.value == r["expected_class"]
    # Retrieval accuracy: did the expected fact actually get retrieved?
    retr_ok = None
    if r["expected_fact_id"]:
        retr_ok = any(c.url == GT[r["expected_fact_id"]].source_url
                      for c in out.citations) if out.citations else False
    cite_ok = None
    if out.query_class == QueryClass.FACTUAL:
        cite_ok = bool(out.citations) and not any(
            c.url in ("", None) for c in out.citations)
    leak = "ABCDE1234F" in out.message

    res.append((r, out, class_ok, retr_ok, cite_ok, ms, leak))
    by_cat[r["category"]][1] += 1
    by_cat[r["category"]][0] += int(class_ok)

print(f"{'ID':<5}{'CAT':<15}{'EXPECTED':<14}{'GOT':<14}{'CLS':<5}{'RETR':<6}{'CITE':<6}{'ms':>6}")
for r, out, ok, retr, cite, ms, leak in res:
    f = lambda v: "-" if v is None else ("ok" if v else "FAIL")
    print(f"{r['eval_id']:<5}{r['category']:<15}{r['expected_class']:<14}"
          f"{out.query_class.value:<14}{f(ok):<5}{f(retr):<6}{f(cite):<6}{ms:6.1f}")

print("\n--- by category ---")
for cat, (ok, n) in sorted(by_cat.items()):
    print(f"  {cat:<15} {ok}/{n}")

class_ok_n = sum(1 for r, o, ok, *_ in res if ok)
retr = [x[3] for x in res if x[3] is not None]
cite = [x[4] for x in res if x[4] is not None]
adv = [x for x in res if x[0]["category"] == "advice"]
lat = sorted(x[5] for x in res)

print("\n--- metrics ---")
print(f"  Routing accuracy      {class_ok_n}/{len(res)}  ({100*class_ok_n/len(res):.0f}%)")
print(f"  Retrieval accuracy    {sum(retr)}/{len(retr)}  ({100*sum(retr)/len(retr):.0f}%)")
print(f"  Citation present      {sum(cite)}/{len(cite)}" + (f"  ({100*sum(cite)/len(cite):.0f}%)" if cite else ""))
print(f"  Refusal accuracy      {sum(1 for x in adv if x[2])}/{len(adv)}")
print(f"  PII leaks             {sum(1 for x in res if x[6])}  (target 0)")
print(f"  Latency p50 / p95     {lat[len(lat)//2]:.1f}ms / {lat[int(len(lat)*.95)]:.1f}ms")
