"""
Feasibility answering (D043).

"Can I invest Rs. 500 every month?" is a factual question with a factual
answer: compare the stated amount against the documented minimum for that
frequency. That is disclosure, not advice.

Deliberate wording choice: the answer never opens with "Yes". Evaluating
an amount against a published minimum is factual, but a bare "Yes" at the
front of a sentence about investing reads as endorsement. "Rs. 500 is
permitted for a monthly SIP if..." carries the same information with no
accidental recommendation.
"""
import re

AMOUNT = re.compile(r"(?:rs\.?|₹|inr)\s*([\d,]+)|\b([\d,]{3,})\s*(?:rupees|rs|/-)?\b", re.I)
FREQ = {
    "daily":       (500, 12, r"\bdaily\b|\bevery day\b|\bper day\b|\broz\b"),
    "weekly":      (500, 12, r"\bweekly\b|\bevery week\b|\bper week\b"),
    "monthly":     (500, 12, r"\bmonthly\b|\bevery month\b|\bper month\b|\ba month\b|\bhar mahine\b"),
    "quarterly":   (1500, 12, r"\bquarterly\b|\bevery quarter\b"),
    "semi-annual": (3000, 4, r"\bsemi.?annual\b|\bhalf.?year\b"),
    "annual":      (5000, 4, r"\bannual\b|\byearly\b|\bevery year\b"),
}
# Flexicap monthly has two tiers; the low tier needs more instalments.
MONTHLY_TIERS = [(1000, 6), (500, 12)]


def parse_amount(text: str) -> int | None:
    m = AMOUNT.search(text)
    if not m:
        return None
    raw = m.group(1) or m.group(2)
    try:
        return int(raw.replace(",", ""))
    except ValueError:
        return None


def parse_frequency(text: str) -> str | None:
    for name, (_, _, pat) in FREQ.items():
        if re.search(pat, text, re.I):
            return name
    return None


def assess_sip(scheme: str, amount: int | None, freq: str | None) -> str | None:
    """Returns a factual feasibility sentence, or None if not applicable."""
    if amount is None:
        return None
    freq = freq or "monthly"

    if freq == "monthly":
        allowed = [(a, n) for a, n in MONTHLY_TIERS if amount >= a]
        if not allowed:
            return (f"Rs. {amount:,} is below the documented monthly SIP minimum for "
                    f"{scheme}, which is Rs. 1,000 for at least 6 instalments or "
                    f"Rs. 500 for at least 12 instalments.")
        a, n = min(allowed, key=lambda t: t[1])
        return (f"Rs. {amount:,} is permitted for a monthly SIP in {scheme}, with a "
                f"commitment of at least {n} instalments.")

    minimum, insts, _ = FREQ[freq]
    if amount < minimum:
        return (f"Rs. {amount:,} is below the documented {freq} SIP minimum for "
                f"{scheme}, which is Rs. {minimum:,}.")
    return (f"Rs. {amount:,} is permitted for a {freq} SIP in {scheme}, with a "
            f"commitment of at least {insts} instalments.")
