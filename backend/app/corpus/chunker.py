"""
Chunking (D005). Structure-aware rather than fixed-window.

KIM and factsheet facts live in label/value pairs and small tables. A
naive character window splits "Minimum SIP" from "Rs. 500", which is the
R7 failure: an answer that is wrong in a way the citation does not catch.
So we split on section boundaries and keep label/value lines intact.
"""
import re
from app.schemas import Chunk, FactType

SECTION_RE = re.compile(r"^\s*(?:[A-Z][A-Z \-/&]{4,}|\d+\.\s+[A-Z][\w \-]+)\s*$", re.M)
LABEL_VALUE_RE = re.compile(r"^\s*([A-Za-z][\w \-/()]{2,40})\s*[:\-]\s*(.+)$")

MAX_CHARS = 900
MIN_CHARS = 80


def split_sections(text: str) -> list[tuple[str, str]]:
    marks = [(m.start(), m.group().strip()) for m in SECTION_RE.finditer(text)]
    if not marks:
        return [("", text)]
    out = []
    for i, (pos, head) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        body = text[pos + len(head):end].strip()
        if body:
            out.append((head, body))
    return out


def _pack(section: str, body: str) -> list[str]:
    """Pack lines up to MAX_CHARS without splitting a label/value pair."""
    lines, buf, out = body.splitlines(), [], []
    size = 0
    for line in lines:
        if size + len(line) > MAX_CHARS and size >= MIN_CHARS:
            out.append("\n".join(buf)); buf, size = [], 0
        buf.append(line); size += len(line) + 1
    if buf:
        tail = "\n".join(buf)
        if out and len(tail) < MIN_CHARS:
            out[-1] += "\n" + tail      # never emit a stranded fragment
        else:
            out.append(tail)
    return out


def chunk_document(text: str, *, document_id: str, source_url: str,
                   source_organization: str, tier: int, scheme_id: str | None,
                   topic: str, fact_type: FactType, document_date: str | None = None,
                   date_collected: str | None = None) -> list[Chunk]:
    chunks: list[Chunk] = []
    for section, body in split_sections(text):
        for i, piece in enumerate(_pack(section, body)):
            header = f"[{section}] " if section else ""
            chunks.append(Chunk(
                chunk_id=f"{document_id}::{len(chunks):03d}",
                text=(header + piece).strip(),
                document_id=document_id, source_url=source_url,
                source_organization=source_organization, tier=tier,
                scheme_id=scheme_id, topic=topic, fact_type=fact_type,
                document_date=document_date, date_collected=date_collected,
                section=section or None,
            ))
    return chunks


def audit_labels(chunks: list[Chunk]) -> list[str]:
    """Quality gate for R7: flag label/value pairs that got separated."""
    problems = []
    for c in chunks:
        for line in c.text.splitlines():
            m = LABEL_VALUE_RE.match(line)
            if m and not m.group(2).strip():
                problems.append(f"{c.chunk_id}: label '{m.group(1)}' has no value")
    return problems
