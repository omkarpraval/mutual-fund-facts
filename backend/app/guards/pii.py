"""
Input PII guard powered by Microsoft Presidio Analyzer and Anonymizer.
Runs FIRST, before logging or any model call (D008).

Deterministic and compliant by design. Incorporates custom Indian
financial recognizers (PAN, Aadhaar, Indian mobile numbers, OTPs, bank accounts).
"""
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine

MESSAGE = (
    "Please don't share personal or account information. This assistant "
    "only handles general mutual fund facts from official sources."
)

# 1. Custom India-specific and financial Pattern Recognizers
_PAN_PATTERN = Pattern(
    name="in_pan_pattern",
    regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    score=1.0
)
_in_pan_recognizer = PatternRecognizer(
    supported_entity="IN_PAN",
    patterns=[_PAN_PATTERN],
    supported_language="en"
)

_AADHAAR_PATTERN = Pattern(
    name="in_aadhaar_pattern",
    regex=r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b",
    score=1.0
)
_in_aadhaar_recognizer = PatternRecognizer(
    supported_entity="IN_AADHAAR",
    patterns=[_AADHAAR_PATTERN],
    supported_language="en"
)

_PHONE_PATTERN = Pattern(
    name="in_phone_pattern",
    regex=r"(?<!\d)(?:\+?91[ -]?)?[6-9]\d{9}(?!\d)",
    score=1.0
)
_in_phone_recognizer = PatternRecognizer(
    supported_entity="IN_PHONE",
    patterns=[_PHONE_PATTERN],
    supported_language="en"
)

_ACCOUNT_PATTERN = Pattern(
    name="in_account_pattern",
    regex=r"\b\d{11,18}\b",
    score=0.9
)
_in_account_recognizer = PatternRecognizer(
    supported_entity="IN_BANK_ACCOUNT",
    patterns=[_ACCOUNT_PATTERN],
    supported_language="en"
)

_OTP_PATTERN_1 = Pattern(
    name="in_otp_pattern_1",
    regex=r"\b(otp|one[ -]?time[ -]?password|passcode|pin)\b\D{0,15}\d{4,8}\b",
    score=1.0
)
_OTP_PATTERN_2 = Pattern(
    name="in_otp_pattern_2",
    regex=r"\b\d{4,8}\D{0,15}\b(otp|passcode)\b",
    score=1.0
)
_in_otp_recognizer = PatternRecognizer(
    supported_entity="IN_OTP",
    patterns=[_OTP_PATTERN_1, _OTP_PATTERN_2],
    supported_language="en"
)

# 2. Build Presidio AnalyzerEngine
_analyzer = AnalyzerEngine()
_analyzer.registry.add_recognizer(_in_pan_recognizer)
_analyzer.registry.add_recognizer(_in_aadhaar_recognizer)
_analyzer.registry.add_recognizer(_in_phone_recognizer)
_analyzer.registry.add_recognizer(_in_account_recognizer)
_analyzer.registry.add_recognizer(_in_otp_recognizer)

_anonymizer = AnonymizerEngine()

# Entities of interest for mutual fund safety
TARGET_ENTITIES = [
    "IN_PAN", "IN_AADHAAR", "IN_PHONE", "IN_BANK_ACCOUNT", "IN_OTP",
    "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "CRYPTO", "IBAN_CODE", "IP_ADDRESS"
]


def scan(text: str) -> list[str]:
    """
    Return the KINDS of PII found using Presidio analyzer.
    Never returns the matched values.
    """
    results = _analyzer.analyze(
        text=text,
        entities=TARGET_ENTITIES,
        language="en",
        score_threshold=0.4
    )
    if not results:
        return []
    # Return unique entity types detected
    return list(dict.fromkeys(r.entity_type for r in results))


def is_safe_to_log(text: str) -> bool:
    return len(scan(text)) == 0


def redact(text: str) -> str:
    """Anonymize text using Presidio Anonymizer."""
    results = _analyzer.analyze(
        text=text,
        entities=TARGET_ENTITIES,
        language="en",
        score_threshold=0.4
    )
    if not results:
        return text
    anonymized = _anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text
