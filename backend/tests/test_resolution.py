import sys; sys.path.insert(0, "..")
from app.retrieval.scheme_resolver import SchemeResolver
from app.retrieval.normaliser import detect_topic

R = SchemeResolver("../data/scheme_aliases.csv")

def test_aliases():
    """The D022 case: users type former names, corpus holds new ones."""
    cases = [
        # (question, selector, expected_scheme_id, expected_match_source)
        ("What is the exit load of SBI Bluechip Fund?", None, "SCH-01", "question_alias"),
        ("SBI Blue Chip minimum SIP?",                  None, "SCH-01", "question_alias"),
        ("SBI Large Cap Fund benchmark",                None, "SCH-01", "question_alias"),
        ("SBI Magnum Multicap Fund exit load",          None, "SCH-02", "question_alias"),
        ("SBI Flexicap riskometer",                     None, "SCH-02", "question_alias"),
        ("SBI Long Term Equity Fund lock in",           None, "SCH-03", "question_alias"),
        ("SBI Magnum Taxgain lock-in period",           None, "SCH-03", "question_alias"),
        ("SBI ELSS Tax Saver Fund minimum",             None, "SCH-03", "question_alias"),
        # selector fallback when no scheme named
        ("What is the minimum SIP?",                 "SCH-02", "SCH-02", "selector"),
        # explicit mention overrides the selector
        ("Exit load of SBI Bluechip Fund?",          "SCH-02", "SCH-01", "question_alias"),
        # neither -> must ask, never guess
        ("What is the minimum SIP?",                    None,     None,  "none"),
    ]
    fails = []
    for q, sel, exp_id, exp_src in cases:
        m = R.resolve(q, sel)
        if m.scheme_id != exp_id or m.matched_on != exp_src:
            fails.append((q, f"{exp_id}/{exp_src}", f"{m.scheme_id}/{m.matched_on}"))
    return fails

def test_topics():
    cases = [
        ("What is the minimum SIP?", "min_sip"),
        ("smallest sip i can start with", "min_sip"),
        ("how much does it cost annually", "ter"),
        ("what is the total expense ratio", "ter"),
        ("charge if i redeem early", "exit_load"),
        ("how risky is this fund", "riskometer"),
        ("how long before i can redeem", "lock_in"),
        ("download capital gains statement", "capital_gains_statement"),
        ("what index is it compared against", "benchmark"),
        ("who is the fund manager", None),   # out of scope, correctly unmatched
    ]
    fails = []
    for q, exp in cases:
        got = detect_topic(q)
        if got != exp: fails.append((q, exp, got))
    return fails

if __name__ == "__main__":
    total = 0
    for name, fn in [("Alias resolution (D022)", test_aliases),
                     ("Topic normalisation", test_topics)]:
        fails = fn()
        total += len(fails)
        print(f"{'PASS' if not fails else 'FAIL'}  {name}")
        for f in fails: print(f"      q={f[0]!r}  expected={f[1]}  got={f[2]}")
    print(f"\n{total} failures")
