"""
Scheme resolution (D003, D018, D022).

All three corpus schemes were renamed under SEBI categorisation. Users
type the old name, the corpus carries the new one. Alias matching runs
BEFORE any embedding similarity, because a rename must never be left to
semantic luck: a scheme mismatch produces a confident wrong answer
rather than a visible failure.

Resolution order:
  1. explicit alias or canonical match in the question  (overrides selector)
  2. the UI scheme selector
  3. neither -> ask, never guess
"""
import csv
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SchemeMatch:
    scheme_id: str | None
    canonical_name: str | None
    matched_on: str          # "question_alias" | "selector" | "ambiguous" | "none"
    matched_text: str | None
    candidates: list | None = None   # set when matched_on == "ambiguous"


def _normalise(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class SchemeResolver:
    def __init__(self, aliases_csv: str | Path):
        self.schemes: dict[str, dict] = {}
        self._index: list[tuple[str, str]] = []   # (normalised alias, scheme_id)

        with open(aliases_csv, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                sid = row["scheme_id"]
                self.schemes[sid] = row
                names = [row["canonical_name"]]
                if row.get("former_name"):
                    names.append(row["former_name"])
                names += [s for s in row.get("short_forms", "").split(";") if s]
                for n in names:
                    self._index.append((_normalise(n), sid))

        # Longest alias first, so "SBI Large Cap Fund" wins over "SBI Large Cap"
        # and a specific former name is never shadowed by a generic short form.
        self._index.sort(key=lambda t: len(t[0]), reverse=True)

    # Words that name the fund house but not a scheme. On their own they
    # cannot identify a fund, so they must offer a choice rather than
    # guessing or dead-ending on "which scheme?".
    HOUSE_ONLY = {"sbi", "sbi mutual fund", "sbi mf"}

    def resolve(self, question: str, selected_scheme_id: str | None = None) -> SchemeMatch:
        q = _normalise(question)

        for alias, sid in self._index:
            if alias and alias in q:
                return SchemeMatch(sid, self.schemes[sid]["canonical_name"],
                                   "question_alias", alias)

        # House name with no scheme name: ambiguous, so offer the options.
        if any(re.search(rf"\b{re.escape(h)}\b", q) for h in self.HOUSE_ONLY):
            if not selected_scheme_id:
                return SchemeMatch(None, None, "ambiguous", None,
                                   candidates=[{"id": k, "name": v["canonical_name"]}
                                               for k, v in self.schemes.items()])

        if selected_scheme_id and selected_scheme_id in self.schemes:
            return SchemeMatch(selected_scheme_id,
                               self.schemes[selected_scheme_id]["canonical_name"],
                               "selector", None)

        return SchemeMatch(None, None, "none", None)

    def canonical(self, scheme_id: str) -> str:
        return self.schemes[scheme_id]["canonical_name"]

    def was_renamed(self, scheme_id: str) -> bool:
        return bool(self.schemes[scheme_id].get("former_name"))
