"""
Advice guard (D009, revised by D042).

The distinction is grammatical, not keyword-based:

  PERMISSION / CAPABILITY  -> factual
    "can I", "could I", "am I allowed", "is it possible", "does it permit"
    These ask what the official documents say. Answering them is disclosure.

  RECOMMENDATION           -> advice
    "should I", "ought I", "is it wise", "good idea", "better", "best",
    "suitable for me", "worth it"
    These ask for judgement. Answering them is advice.

The old rule put "can" alongside "should" in one pattern, so every
feasibility question was refused: "Can I invest Rs. 500 monthly?",
"Can I redeem after 3 years?", "Can I invest less than Rs. 5,000?". A
facts-only product refusing to state facts is the worst failure it has.

Ambiguity still resolves to refusal. A permission question with no
detectable factual topic ("Can I invest in this fund?") is treated as
advice, because there is nothing factual being asked for.
"""
import re
from app.schemas import RefusalKind

# Checked first. If any of these fire, it is advice regardless of phrasing.
RECOMMENDATION: list[tuple[RefusalKind, re.Pattern]] = [
    (RefusalKind.PERSONAL_FINANCE, re.compile(
        r"\bi (am|'m) \d+ years old\b|\bi earn\b|\bmy (salary|income)\b"
        r"|\bi have\s+(rs\.?|₹|inr)?\s?[\d,]+\s*(lakh|crore|k)?\b.{0,40}\b(invest|put|do with)\b"
        r"|\bfor my (retirement|child|goal|house|tax planning)\b"
        r"|\bsuitable for me\b|\bright for me\b|\benough for my\b"
        r"|\bcan i handle\b|\bfor my (financial )?goals?\b", re.I)),
    (RefusalKind.BUY_SELL, re.compile(
        r"\b(should|shall|ought|must)\s+i\s+(buy|sell|invest|exit|redeem|switch|hold|put|start|move|withdraw|stay|continue|stop)\b"
        r"|\bis it (a )?(good|bad|wise|smart|sensible)\b"
        r"|\b(a|an) (good|bad|wise|smart|sensible) (idea|choice|option|move)\b"
        r"|\b(worth|good time)\s+(buying|investing|to invest|to buy)\b"
        r"|\bdo you recommend\b|\bwhat do you (think|suggest)\b"
        r"|\blena chahiye\b|\bbech(na)? chahiye\b|\bkarna chahiye\b", re.I)),
    (RefusalKind.RETURN_PREDICTION, re.compile(
        r"\b(will|would|going to)\b.{0,30}\b(return|outperform|beat|grow|give|make)\b"
        r"|\bexpected returns?\b|\bfuture (performance|returns?)\b"
        r"|\bhow much will i (make|get|earn)\b|\bguarantee\b"
        r"|\b(outperform|lose money|make money|profit|double my money)\b"
        r"|\bbeat\b.{0,20}\b(market|benchmark|index)\b", re.I)),
    (RefusalKind.FUND_SELECTION, re.compile(
        r"\bwhich\b.{0,30}\b(fund|scheme|one|option|amount|plan|frequency)s?\b.{0,40}\b(better|best|should|pick|choose|recommend|prefer)\b"
        r"|\b(best|better)\b.{0,15}\b(fund|scheme|option)s?\b"
        r"|\b(fund|scheme|one)s?\b.{0,25}\bis (the )?(better|best)\b"
        r"|\bis\b.{0,30}\bbetter than\b"
        r"|\bwhich\b.{0,30}\b(fund|scheme|one)s?\b.{0,30}\b(lower|higher|less|more|cheaper|safer)\b"
        r"|\brecommend (a|an|any|some) (fund|scheme)\b", re.I)),
    (RefusalKind.PORTFOLIO, re.compile(
        r"\b(build|make|review|rebalance|allocate)\b.{0,25}\b(portfolio|allocation)\b"
        r"|\bhow much should i invest\b|\basset allocation\b"
        r"|\ball (of )?my money\b", re.I)),
]

# Permission framing. Factual IF a concrete topic was also detected.
PERMISSION = re.compile(
    r"\b(can|could|may)\s+i\b|\bam i (allowed|able|permitted)\b"
    r"|\bis it (possible|allowed|permitted)\b|\bdoes (it|the scheme|this fund) (allow|permit|accept)\b"
    r"|\bis\s+(rs\.?\s*)?[\d,]+\s*(allowed|permitted|accepted)\b"
    r"|\bsakta hoon\b|\bsakte hain\b", re.I)

REDIRECTS = {
    RefusalKind.BUY_SELL: "the scheme's riskometer and benchmark",
    RefusalKind.FUND_SELECTION: "the factual details of each scheme separately",
    RefusalKind.PORTFOLIO: "the scheme's stated investment objective and category",
    RefusalKind.RETURN_PREDICTION: "the official factsheet, which carries past performance",
    RefusalKind.PERSONAL_FINANCE: "the scheme's minimum investment and lock-in details",
}


def detect(text: str, topic: str | None = None) -> RefusalKind | None:
    for kind, pat in RECOMMENDATION:
        if pat.search(text):
            return kind

    if PERMISSION.search(text):
        # Permitted-under-the-rules question with a real factual target.
        return None if topic else RefusalKind.BUY_SELL

    return None


def refusal_message(kind: RefusalKind) -> str:
    return (
        "I can give you factual information from official sources, but I can't "
        f"advise on this. You may find {REDIRECTS[kind]} useful for deciding yourself."
    )
