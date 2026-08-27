"""
LLM intent normalisation (D041).

Placed deliberately: AFTER the PII and advice guards, BEFORE retrieval.

Why after the guards. Sending a message to a third-party API to work out
its intent would defeat D008 entirely if that message contained a PAN.
The guards run first and the LLM never sees a blocked message. This
ordering is not negotiable and is asserted in the tests.

Why before retrieval. The failures this fixes were retrieval misses, not
writing problems: "Flexicap se paisa jaldi nikalne pe charges lagenge?"
never reached a chunk, so a better generator would have had nothing to
work from.

Two safeguards on the classifier itself:

1. CLOSED ENUM including "none". An unconstrained classifier invents a
   plausible topic for out-of-scope questions, which would quietly destroy
   the refusal behaviour that is currently at 100%. "none" means
   no-evidence, exactly as an unmatched deterministic lookup does.

2. DETERMINISTIC FIRST. This runs only when the synonym lookup returns
   nothing. Most queries then cost no latency and no quota, and free-tier
   rate limits stop being a demo risk.
"""
import json, os, urllib.request
from app.retrieval.normaliser import TOPIC_SYNONYMS, detect_topic

TOPICS = sorted(TOPIC_SYNONYMS.keys())
TIMEOUT = 8

SYSTEM = (
    "You classify a retail investor's question about a mutual fund scheme "
    "into exactly one topic key. Reply with the key alone, no punctuation "
    "or explanation.\n\n"
    "Valid keys:\n" + "\n".join(f"- {t}" for t in TOPICS) + "\n- none\n\n"
    "Use 'none' if the question does not map cleanly to one of the keys, "
    "including questions about fund managers, AUM, past returns, NAV, or "
    "anything not listed. Do not guess. Questions may be in English, Hindi, "
    "or a mix of both."
)


def _groq_classify(question: str) -> str | None:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    body = json.dumps({
        "model": "llama-3.1-8b-instant",
        "temperature": 0,
        "max_tokens": 12,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": question}],
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        out = json.loads(r.read())
    return out["choices"][0]["message"]["content"].strip().lower()


def resolve_topic(question: str, classifier=None) -> tuple[str | None, str]:
    """
    Returns (topic, how). `how` is one of "lookup", "llm", "unmatched",
    so the source of every classification stays visible in eval output.
    """
    topic = detect_topic(question)
    if topic:
        return topic, "lookup"

    fn = classifier or _groq_classify
    try:
        guess = fn(question)
    except Exception:
        return None, "unmatched"       # degrade to no-evidence, never guess

    # The enum is enforced here, not trusted to the model.
    if guess in TOPICS:
        return guess, "llm"
    return None, "unmatched"
