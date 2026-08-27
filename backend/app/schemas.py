"""Core data shapes. Kept deliberately small and explicit."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FactType(str, Enum):
    STATIC = "static"
    DYNAMIC_DAILY = "dynamic_daily"      # TER, disclosed daily (D004)
    DYNAMIC_MONTHLY = "dynamic_monthly"  # riskometer, monthly cycle (D004)


# Staleness windows, per D019. Deliberately looser than the disclosure
# cadence so a week-old corpus still demonstrates the normal answer path.
STALENESS_DAYS = {
    FactType.DYNAMIC_DAILY: 7,
    FactType.DYNAMIC_MONTHLY: 45,
    FactType.STATIC: None,
}


class QueryClass(str, Enum):
    FACTUAL = "factual"
    ADVICE = "advice"
    PII = "pii"
    NEEDS_SCHEME = "needs_scheme"
    OUT_OF_SCOPE = "out_of_scope"


class RefusalKind(str, Enum):
    BUY_SELL = "buy_sell"
    FUND_SELECTION = "fund_selection"
    PORTFOLIO = "portfolio"
    RETURN_PREDICTION = "return_prediction"
    PERSONAL_FINANCE = "personal_finance"


@dataclass
class Chunk:
    chunk_id: str
    text: str
    document_id: str
    source_url: str
    source_organization: str
    tier: int
    scheme_id: Optional[str]
    topic: str
    fact_type: FactType
    document_date: Optional[str] = None   # when the source doc was published
    date_collected: Optional[str] = None  # when we retrieved it
    fact_as_of: Optional[str] = None      # date the fact itself applies to
    section: Optional[str] = None
    fact_label: Optional[str] = None
    fact_value: Optional[str] = None


@dataclass
class Scheme:
    scheme_id: str
    canonical_name: str
    former_name: Optional[str] = None
    short_forms: list[str] = field(default_factory=list)
