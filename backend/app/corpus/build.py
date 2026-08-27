"""
Build the retrievable corpus from ground_truth.csv.

The verification state decides answerability (D030), and it is enforced
here rather than in the prompt, so a quarantined fact cannot reach the
model at all:

  VERIFIED     -> indexed, answered normally
  CONDITIONAL  -> indexed, answer must carry its condition
  PENDING      -> NOT indexed, registered as a known gap
  CONFLICT     -> NOT indexed, registered as a known gap

A known gap is not the same as an unknown question. Both produce a
no-evidence response, but the gap is deliberate and reportable.
"""
import csv
from dataclasses import dataclass
from pathlib import Path
from app.schemas import Chunk, FactType
from app.corpus.titles import title_for

SCHEME_IDS = {
    "SBI Large Cap Fund": "SCH-01",
    "SBI Flexicap Fund": "SCH-02",
    "SBI ELSS Tax Saver Fund": "SCH-03",
    "NA": None,
}

ANSWERABLE = ("VERIFIED", "CONDITIONAL")


@dataclass
class Gap:
    scheme: str
    fact_key: str
    reason: str


def _state(status: str) -> str:
    return status.split(" -")[0].strip().split()[0].upper()


def load(path: str | Path) -> tuple[list[Chunk], list[Gap]]:
    chunks: list[Chunk] = []
    gaps: list[Gap] = []

    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            state = _state(row["verification_status"])
            value = (row["value"] or "").strip()

            if state not in ANSWERABLE or not value:
                gaps.append(Gap(row["scheme"], row["fact_key"],
                                row["verification_status"]))
                continue

            scheme = row["scheme"]
            label = row["fact_label"]
            # The scheme name is in the text so BM25 can match it, but
            # metadata filtering is what actually enforces scope.
            text = f"{scheme} - {label}: {value}"
            if state == "CONDITIONAL":
                text += f" [condition: {row['verification_status']}]"

            chunks.append(Chunk(
                chunk_id=f"{row['fact_id']}",
                text=text,
                document_id=title_for(row["source_document_id"]),
                source_url=row["source_url"],
                source_organization=("AMFI" if "amfi" in row["source_document_id"]
                                     else "Groww" if "groww" in row["source_document_id"]
                                     else "SBI Mutual Fund"),
                tier=(2 if "amfi" in row["source_document_id"]
                      else 3 if "groww" in row["source_document_id"] else 1),
                scheme_id=SCHEME_IDS.get(scheme),
                topic=row["fact_key"],
                fact_type=FactType(row["fact_type"]),
                document_date=row.get("source_dated") or None,
                date_collected=row.get("retrieved_at") or None,
                fact_as_of=row.get("fact_as_of") or None,
                section=label,
                fact_label=label,
                fact_value=value,
            ))
    return chunks, gaps


def approved_urls(chunks: list[Chunk]) -> set[str]:
    return {c.source_url for c in chunks if c.source_url}
