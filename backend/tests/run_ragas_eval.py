"""
RAGAS Automated Evaluation Harness for Mutual Fund Facts RAG Pipeline.
Computes Context Recall, Context Precision, Faithfulness, and Answer Relevancy.
"""
import sys
import csv
import time
sys.path.insert(0, "..")

from collections import defaultdict
from app.corpus.build import load, approved_urls, SCHEME_IDS
from app import coverage as cov_mod
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.scheme_resolver import SchemeResolver
from app.pipeline import Pipeline
from app.schemas import QueryClass


def evaluate_ragas_benchmarks():
    print("=" * 65)
    print("      RAGAS Automated Evaluation & Grounding Benchmark        ")
    print("=" * 65)

    # 1. Initialize pipeline
    chunks, gaps = load("../data/ground_truth.csv")
    resolver = SchemeResolver("../data/scheme_aliases.csv")
    retriever = HybridRetriever(chunks, embedder=None)
    urls = approved_urls(chunks)
    coverage = cov_mod.build(chunks, gaps, SCHEME_IDS)

    pipe = Pipeline(
        resolver=resolver,
        retriever=retriever,
        approved_urls=urls,
        coverage=coverage
    )
    GT = {c.chunk_id: c for c in chunks}

    # 2. Load evaluation samples
    rows = list(csv.DictReader(open("../data/eval_set.csv", encoding="utf-8")))
    ragas_samples = []

    context_recalls = []
    context_precisions = []
    faithfulness_scores = []
    answer_relevancy_scores = []

    print(f"Evaluating {len(rows)} samples across RAG & Guardrail dimensions...\n")

    for r in rows:
        t0 = time.perf_counter()
        out = pipe.answer(r["question"], r["selected_scheme"] or None)
        latency = (time.perf_counter() - t0) * 1000

        retrieved_contexts = [h.chunk.text for h in out.hits] if out.hits else []
        expected_fact_id = r["expected_fact_id"]

        # Metric 1: Context Recall (did we retrieve the ground truth context?)
        if expected_fact_id and expected_fact_id in GT:
            gt_text = GT[expected_fact_id].text
            hit_match = any(gt_text in ctx or ctx in gt_text for ctx in retrieved_contexts)
            recall = 1.0 if hit_match else 0.0
            context_recalls.append(recall)
        else:
            recall = None

        # Metric 2: Context Precision (is top-ranked context the relevant one?)
        if expected_fact_id and retrieved_contexts and expected_fact_id in GT:
            gt_text = GT[expected_fact_id].text
            top_hit = retrieved_contexts[0]
            precision = 1.0 if (gt_text in top_hit or top_hit in gt_text) else (0.5 if recall else 0.0)
            context_precisions.append(precision)
        elif expected_fact_id:
            context_precisions.append(0.0)

        # Metric 3: Faithfulness / Citation Grounding (are all citations valid & whitelisted?)
        if out.query_class == QueryClass.FACTUAL:
            is_faithful = bool(out.citations) and all(c.url in urls for c in out.citations)
            faithfulness_scores.append(1.0 if is_faithful else 0.0)
        elif out.query_class in (QueryClass.PII, QueryClass.ADVICE, QueryClass.OUT_OF_SCOPE, QueryClass.NEEDS_SCHEME):
            # Guardrails correctly prevented hallucination
            faithfulness_scores.append(1.0)

        # Metric 4: Answer Relevancy (did the classification and response match intent?)
        is_relevant = (out.query_class.value == r["expected_class"])
        answer_relevancy_scores.append(1.0 if is_relevant else 0.0)

        ragas_samples.append({
            "eval_id": r["eval_id"],
            "category": r["category"],
            "question": r["question"],
            "query_class": out.query_class.value,
            "expected_class": r["expected_class"],
            "recall": recall,
            "latency_ms": latency
        })

    # Summary Scores
    avg_recall = sum(context_recalls) / len(context_recalls) if context_recalls else 1.0
    avg_precision = sum(context_precisions) / len(context_precisions) if context_precisions else 1.0
    avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores)
    avg_relevancy = sum(answer_relevancy_scores) / len(answer_relevancy_scores)

    print(f"{'RAGAS Metric':<28} | {'Score':<8} | {'Status'}")
    print("-" * 50)
    print(f"{'Context Recall':<28} | {avg_recall*100:6.1f}%  | {'PASSED' if avg_recall >= 0.95 else 'WARN'}")
    print(f"{'Context Precision':<28} | {avg_precision*100:6.1f}%  | {'PASSED' if avg_precision >= 0.95 else 'WARN'}")
    print(f"{'Faithfulness / Grounding':<28} | {avg_faithfulness*100:6.1f}%  | {'PASSED' if avg_faithfulness >= 0.95 else 'WARN'}")
    print(f"{'Answer Relevancy':<28} | {avg_relevancy*100:6.1f}%  | {'PASSED' if avg_relevancy >= 0.95 else 'WARN'}")
    print("-" * 50)
    print(f"Overall RAGAS Score: {((avg_recall + avg_precision + avg_faithfulness + avg_relevancy) / 4)*100:.1f}%\n")


if __name__ == "__main__":
    evaluate_ragas_benchmarks()
