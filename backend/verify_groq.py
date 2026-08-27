"""
Run this on your machine to verify the Groq classifier end to end.
The build sandbox cannot reach api.groq.com, so this check is yours.

    export GROQ_API_KEY=...          # Windows: set GROQ_API_KEY=...
    python verify_groq.py
"""
import os, sys
sys.path.insert(0, ".")
from app.retrieval.intent import _groq_classify, resolve_topic

if not os.environ.get("GROQ_API_KEY"):
    print("GROQ_API_KEY is not set. Set it and run again.")
    raise SystemExit(1)

# Questions with no deterministic synonym match, so the classifier is
# genuinely exercised. The last three MUST come back as none.
CASES = [
    ("kitne saal tak paisa fasa rahega isme",        "lock_in"),
    ("agar main 2 saal me nikal loon to kya hoga",   "exit_load"),
    ("yearly kitna percent kat ta hai",              "ter"),
    ("what index does this get compared against",    "benchmark"),
    ("how dangerous is this scheme supposed to be",  "riskometer"),
    ("who manages this fund day to day",             None),
    ("what were the returns over five years",        None),
    ("what is the NAV right now",                    None),
]

ok = 0
for q, expected in CASES:
    topic, how = resolve_topic(q)
    good = topic == expected
    ok += good
    print(f"  {'ok  ' if good else 'FAIL'} [{how:9s}] {str(topic):12s} expected {expected}  | {q}")

print(f"\n{ok}/{len(CASES)} correct")
print("\nThe three 'None' cases matter most. If the classifier invents a topic")
print("for them, out-of-scope questions stop being refused, and refusal")
print("accuracy is currently 100%. Report the result before we keep it on.")
