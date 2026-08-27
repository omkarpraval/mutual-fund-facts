"""Staleness handling for dynamic facts (D004, D019)."""
from datetime import date, datetime
from app.schemas import FactType, STALENESS_DAYS

CADENCE_NOTE = {
    FactType.DYNAMIC_DAILY: "TER is disclosed daily by the AMC and on the AMFI website.",
    FactType.DYNAMIC_MONTHLY: "The riskometer is reviewed monthly and published "
                              "within 10 days of month end.",
}

STALE_NOTE = ("This may not be the current value. Please check the official "
              "disclosure page linked above for the latest figure.")


def days_old(collected: str, today: date | None = None) -> int:
    d = datetime.strptime(collected, "%Y-%m-%d").date()
    return ((today or date.today()) - d).days


def is_stale(fact_type: FactType, collected: str, today: date | None = None) -> bool:
    window = STALENESS_DAYS.get(fact_type)
    return False if window is None else days_old(collected, today) > window


def annotate(answer: str, fact_type: FactType, collected: str,
             today: date | None = None) -> str:
    if fact_type == FactType.STATIC:
        return answer
    parts = [answer, CADENCE_NOTE.get(fact_type, "")]
    if is_stale(fact_type, collected, today):
        parts.append(STALE_NOTE)
    return " ".join(p for p in parts if p)
