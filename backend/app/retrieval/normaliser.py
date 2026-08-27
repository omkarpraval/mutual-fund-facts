"""
Query normalisation. Maps the many ways users phrase the same fact
onto a canonical topic key, so retrieval and metadata filtering agree.
"""
import re

TOPIC_SYNONYMS = {
    "min_sip": ["minimum sip", "min sip", "smallest sip", "lowest sip",
                "minimum systematic investment", "monthly sip amount",
                "how much sip", "sip amount", "start sip with",
                "every month", "per month", "monthly investment",
                "har mahine", "mahine me", "sip kitna", "kitna sip",
                "invest monthly", "put every month", "monthly minimum",
                "daily sip", "weekly sip", "monthly sip", "quarterly sip",
                "annual sip", "yearly sip", "semi annual sip",
                "sip instalment", "sip installment", "number of instalments"],
    "min_lumpsum": ["minimum investment", "minimum lumpsum", "min lumpsum",
                    "one time investment", "minimum amount", "lump sum",
                    "need to start", "how much to start", "start with",
                    "invest less than", "minimum to invest", "kitna minimum",
                    "shuru karne", "one shot"],
    "additional_purchase": ["additional purchase", "additional investment",
                            "top up amount", "add more"],
    "exit_load": ["exit load", "redemption charge", "exit charge",
                  "penalty for redeeming", "charge if i redeem",
                  "charge me if i redeem", "redeem early", "exit early",
                  "charge if i exit", "penalty", "load structure",
                  "withdrawal charge", "withdrawal charges", "charge to withdraw",
                  "paisa nikalne", "nikalne pe charge", "jaldi nikalne",
                  "paise nikalne", "withdraw early", "take money out early",
                  "redeem karne", "redeem karne ka charge", "nikalne ka charge",
                  "beech mein redeem", "charges when i withdraw",
                  "pay anything when redeeming", "anything when i redeem",
                  "redeem units", "redeem my units", "withdraw units",
                  "redemption rules", "when can i withdraw"],
    "ter": ["expense ratio", "ter", "total expense ratio", "annual charge",
            "how much does it cost", "fund charges", "management fee",
            "fund fee", "annual fee", "yearly charge", "kitna charge lagta",
            "cost of the fund", "what does it charge",
            "charges for", "charges of", "what are the charges",
            "fund ke charges", "charges kya",
            "fund expenses", "scheme expenses", "expenses of the fund",
            "expense ratio pls", "what are the expenses"],
    "riskometer": ["riskometer", "risk o meter", "risk level", "how risky",
                   "risk rating", "risk classification", "high risk",
                   "risky is this", "risk category", "risk ka level",
                   "riskometer kya", "is this fund risky"],
    "benchmark": ["benchmark", "index it tracks", "compared against",
                  "benchmark index", "additional benchmark",
                  "index does it track", "which index", "tracks which index",
                  "measured against", "index it follows"],
    "lock_in": ["lock in", "lockin", "locked", "lock-in period",
                "how long before i can redeem", "three year",
                "redeem after", "withdraw after", "redeem before",
                "kitne saal", "saal tak", "tax benefit", "80c"],
    "investment_objective": ["investment objective", "objective", "what does it invest in",
                             "aim of the fund", "what is this fund"],
    "scheme_category": ["category", "sebi category", "type of fund", "what kind of fund"],
    "capital_gains_statement": ["capital gains statement", "capital gain statement",
                                "tax statement", "tax p&l", "download statement",
                                "statement for itr", "gains report"],
}

_LOOKUP = [(phrase, topic) for topic, ps in TOPIC_SYNONYMS.items() for phrase in ps]
_LOOKUP.sort(key=lambda t: len(t[0]), reverse=True)


def normalise(question: str) -> str:
    q = re.sub(r"[^a-z0-9 ]", " ", question.lower())
    q = re.sub(r"\s+", " ", q).strip()
    return q


def detect_topic(question: str) -> str | None:
    q = normalise(question)
    for phrase, topic in _LOOKUP:
        if phrase in q:
            return topic
    return None


def topic_of(question: str) -> str | None:
    """
    Deterministic topic, with an entity assist: an amount plus a frequency
    is a SIP question by construction even when no synonym phrase matches
    ("Can I invest 200 monthly?"). Used for both whole questions and
    individual clauses so the two never disagree.
    """
    from app.feasibility import parse_amount, parse_frequency
    t = detect_topic(question)
    freq = parse_frequency(question)
    # An explicit frequency outranks a lumpsum phrase: "start with Rs. 500
    # monthly" is a SIP question even though "start with" reads as lumpsum.
    if freq and t in (None, "min_lumpsum"):
        return "min_sip"
    if t:
        return t
    if parse_amount(question) is not None:
        return "min_sip" if freq else "min_lumpsum"
    return None
