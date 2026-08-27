"""
Citation validation (D006).

The citation must point at the evidence actually used, not a homepage.
One primary source by default; a supporting source only when the answer
genuinely spans two facts no single document covers.
"""
from dataclasses import dataclass
from app.schemas import Chunk

GENERIC = ("/", "/home", "/index", "/mutual-fund", "/help")


@dataclass
class Citation:
    title: str
    url: str
    organization: str
    last_updated: str | None      # kept for compatibility
    fact_as_of: str | None = None
    source_dated: str | None = None
    retrieved_at: str | None = None


def _too_generic(url: str) -> bool:
    path = url.split("//", 1)[-1]
    path = path[path.find("/"):] if "/" in path else "/"
    return path.rstrip("/") in [g.rstrip("/") for g in GENERIC]


def build(used: list[Chunk], allow_supporting: bool = False) -> list[Citation]:
    if not used:
        return []
    seen, out = set(), []
    for c in used:
        if c.source_url in seen or _too_generic(c.source_url):
            continue
        seen.add(c.source_url)
        out.append(Citation(c.document_id, c.source_url, c.source_organization,
                            c.fact_as_of or c.document_date or c.date_collected,
                            c.fact_as_of, c.document_date, c.date_collected))
        if len(out) == (2 if allow_supporting else 1):
            break
    return out


def validate(citations: list[Citation], approved_urls: set[str]) -> list[str]:
    """Every citation must resolve to an approved corpus source."""
    return [c.url for c in citations if c.url not in approved_urls]
