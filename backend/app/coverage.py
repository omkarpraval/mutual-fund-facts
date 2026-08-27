"""
Coverage map (D044).

We already know, per scheme, which facts are verified and which are
quarantined. The interface was throwing that away and saying "not in my
sources" for everything, which makes a deliberate, documented gap look
like a broken system.

"I don't understand the question" and "I understand exactly and that fact
is not verified for this scheme" are different answers and deserve
different words.
"""
from dataclasses import dataclass

LABELS = {
    "min_sip": "Minimum SIP", "min_lumpsum": "Minimum investment",
    "additional_purchase": "Additional purchase", "exit_load": "Exit load",
    "ter_regular": "Expense ratio (Regular)", "ter_direct": "Expense ratio (Direct)",
    "benchmark": "Benchmark", "riskometer": "Riskometer", "lock_in": "Lock-in",
    "investment_objective": "Investment objective", "scheme_category": "Category",
    "scheme_type": "Scheme type", "inception_date": "Inception date",
}


@dataclass
class Coverage:
    have: dict[str, list[str]]      # scheme_id -> topics available
    gaps: dict[str, list[str]]      # scheme_id -> topics known-missing


def build(chunks, gap_rows, scheme_ids: dict) -> Coverage:
    have: dict[str, list[str]] = {}
    for c in chunks:
        have.setdefault(c.scheme_id or "GENERAL", []).append(c.topic)
    gaps: dict[str, list[str]] = {}
    for g in gap_rows:
        sid = scheme_ids.get(g.scheme, "GENERAL")
        gaps.setdefault(sid, []).append(g.fact_key)
    return Coverage(have, gaps)


def label(topic: str) -> str:
    return LABELS.get(topic, topic.replace("_", " "))


COLUMNS = [
    {"topic": "scheme_type", "label": "Scheme type", "abbr": "Type"},
    {"topic": "scheme_category", "label": "Category", "abbr": "Cat"},
    {"topic": "investment_objective", "label": "Investment objective", "abbr": "Objective"},
    {"topic": "min_lumpsum", "label": "Minimum investment", "abbr": "Min inv"},
    {"topic": "min_sip", "label": "Minimum SIP", "abbr": "Min SIP"},
    {"topic": "additional_purchase", "label": "Additional purchase", "abbr": "Addl"},
    {"topic": "exit_load", "label": "Exit load", "abbr": "Exit"},
    {"topic": "lock_in", "label": "Lock-in", "abbr": "Lock-in"},
    {"topic": "ter_regular", "label": "Expense ratio (Regular)", "abbr": "TER (R)"},
    {"topic": "ter_direct", "label": "Expense ratio (Direct)", "abbr": "TER (D)"},
    {"topic": "benchmark", "label": "Benchmark", "abbr": "Bench"},
    {"topic": "riskometer", "label": "Riskometer", "abbr": "Risk"},
]


def full_coverage(cov: Coverage, schemes: dict) -> dict:
    columns = [{"topic": col["topic"], "label": col["label"]} for col in COLUMNS]
    rows = []

    for sid, info in schemes.items():
        have_topics = set(cov.have.get(sid, []))
        cells = []

        for col in COLUMNS:
            topic = col["topic"]
            if topic == "lock_in" and sid != "SCH-03":
                state = "na"
            elif sid == "SCH-03" and topic == "riskometer":
                state = "conditional"
            elif topic in have_topics:
                state = "verified"
            else:
                state = "gap"

            cells.append({
                "topic": topic,
                "label": col["label"],
                "state": state,
            })

        rows.append({
            "scheme_id": sid,
            "scheme_name": info["canonical_name"],
            "former_name": info["former_name"],
            "cells": cells,
        })

    chips = {sid: available_labels(cov, sid, limit=6) for sid in schemes}
    return {
        "columns": columns,
        "rows": rows,
        "chips": chips,
    }


def available_labels(cov: Coverage, scheme_id: str | None, limit: int = 6) -> list[str]:
    topics = cov.have.get(scheme_id or "GENERAL", [])
    seen, out = set(), []
    for t in topics:
        base = label(t)
        if base not in seen:
            seen.add(base); out.append(base)
    return out[:limit]


def is_known_gap(cov: Coverage, scheme_id: str | None, topic: str | None) -> bool:
    return bool(topic) and topic in cov.gaps.get(scheme_id or "GENERAL", [])
