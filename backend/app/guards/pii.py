"""
Input PII guard. Runs FIRST, before logging or any model call (D008).

Deterministic on purpose. The goal is non-retention, not clever
detection: nothing here ever writes a matched value anywhere.
"""
import re

PATTERNS = {
    "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "Aadhaar": re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"),
    "phone": re.compile(r"(?<!\d)(?:\+?91[ -]?)?[6-9]\d{9}(?!\d)"),
    "account": re.compile(r"\b\d{11,18}\b"),
    # OTPs sit in a gap between the phone and account patterns. Keyed on
    # the label rather than the digits alone, because a bare 4-6 digit
    # number is usually an amount or a year.
    "OTP": re.compile(r"\b(otp|one[ -]?time[ -]?password|passcode|pin)\b\D{0,15}\d{4,8}\b"
                      r"|\b\d{4,8}\D{0,15}\b(otp|passcode)\b", re.I),
}

MESSAGE = (
    "Please don't share personal or account information. This assistant "
    "only handles general mutual fund facts from official sources."
)


def scan(text: str) -> list[str]:
    """Return the KINDS of PII found. Never returns the matched values."""
    return [kind for kind, pat in PATTERNS.items() if pat.search(text)]


def is_safe_to_log(text: str) -> bool:
    return not scan(text)


def redact(text: str) -> str:
    for kind, pat in PATTERNS.items():
        text = pat.sub(f"[{kind}_REDACTED]", text)
    return text
