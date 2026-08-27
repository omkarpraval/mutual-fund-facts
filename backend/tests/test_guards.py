import sys; sys.path.insert(0, "..")
from app.guards import pii, advice
from app.schemas import RefusalKind

def test_pii():
    cases = [
        ("My PAN is ABCDE1234F", ["PAN"]),
        ("aadhaar 1234 5678 9012", ["Aadhaar"]),
        ("mail me at omkar@example.com", ["email"]),
        ("call 9876543210", ["phone"]),
        ("What is the minimum SIP?", []),
        ("Exit load for SBI Flexicap?", []),
        ("Is the expense ratio 1.5%?", []),
    ]
    fails = []
    for text, expected in cases:
        got = pii.scan(text)
        ok = set(got) >= set(expected) and (bool(got) == bool(expected))
        if not ok: fails.append((text, expected, got))
    return fails

def test_no_leak():
    """The guard must never echo the matched value."""
    t = "My PAN is ABCDE1234F"
    return [] if "ABCDE1234F" not in str(pii.scan(t)) else [("leak", t, "value echoed")]

def test_advice():
    cases = [
        ("Should I buy SBI Flexicap Fund?", RefusalKind.BUY_SELL),
        ("Which fund is better for me?", RefusalKind.FUND_SELECTION),
        ("Build me a portfolio", RefusalKind.PORTFOLIO),
        ("Which fund will give higher returns?", RefusalKind.RETURN_PREDICTION),
        ("I have 5 lakh to invest, what should I do with it?", RefusalKind.PERSONAL_FINANCE),
        ("kya ye fund lena chahiye", RefusalKind.BUY_SELL),
        ("What is the exit load?", None),
        ("What is the minimum SIP for SBI Large Cap Fund?", None),
        ("What is the benchmark?", None),
        ("Does this fund have a lock-in?", None),
    ]
    fails = []
    for text, expected in cases:
        got = advice.detect(text)
        if got != expected: fails.append((text, expected, got))
    return fails

if __name__ == "__main__":
    total = 0
    for name, fn in [("PII detection", test_pii), ("PII non-leak", test_no_leak),
                     ("Advice detection", test_advice)]:
        fails = fn()
        total += len(fails)
        print(f"{'PASS' if not fails else 'FAIL'}  {name}")
        for f in fails: print(f"      {f}")
    print(f"\n{total} failures")
