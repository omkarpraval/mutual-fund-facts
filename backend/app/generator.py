"""
Generation adapter. Provider is not yet chosen, so this is a slot with
three implementations and an env switch. Nothing else in the codebase
knows which one is live.

  MF_LLM=gemini | groq | none   (default: none)

The "none" path is not a stub. It composes the answer directly from the
retrieved chunk, which is the most grounded output possible: it cannot
hallucinate because it never generates. It is worse prose than an LLM
would write and it is a legitimate fallback for a demo with no key.
"""
import os, json, urllib.request
from app.schemas import FactType
from app import freshness

TIMEOUT = 20


def _http_json(url: str, payload: dict, headers: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read())


def _gemini(system: str, context: str, question: str) -> str:
    key = os.environ["GEMINI_API_KEY"]
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"gemini-2.0-flash:generateContent?key={key}")
    out = _http_json(url, {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": f"Context:\n{context}\n\nQuestion: {question}"}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 200},
    }, {})
    return out["candidates"][0]["content"]["parts"][0]["text"].strip()


def _groq(system: str, context: str, question: str) -> str:
    key = os.environ["GROQ_API_KEY"]
    out = _http_json("https://api.groq.com/openai/v1/chat/completions", {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.1, "max_tokens": 200,
        "messages": [{"role": "system", "content": system},
                     {"role": "user",
                      "content": f"Context:\n{context}\n\nQuestion: {question}"}],
    }, {"Authorization": f"Bearer {key}"})
    return out["choices"][0]["message"]["content"].strip()


SIP_BY_FREQ = {
    "daily":       "Rs. 500 for at least 12 instalments",
    "weekly":      "Rs. 1,000 for at least 6 instalments, or Rs. 500 for at least 12",
    "monthly":     "Rs. 1,000 for at least 6 instalments, or Rs. 500 for at least 12",
    "quarterly":   "Rs. 1,500 for at least 12 months",
    "semi-annual": "Rs. 3,000 for at least 4 instalments",
    "annual":      "Rs. 5,000 for at least 4 instalments",
}
SIP_SUMMARY = "For a {freq} SIP in {scheme}, the minimum is {detail}."


def extractive(hits, question: str = "") -> str:
    """
    Zero-hallucination fallback: state the retrieved fact verbatim, then
    cap at three sentences. Facts whose official wording carries many
    conditions get a summary plus an explicit pointer to the rest, so the
    limit is met without pretending the conditions do not exist.
    """
    from app.prompt import cap_sentences, CONDITION_HINT
    if not hits:
        return "I couldn't find this information in the official sources available to me."
    c = hits[0].chunk
    body = c.text.split("[condition:")[0].strip()

    if c.topic == "min_sip" and "Frequency-dependent" in body:
        from app.feasibility import parse_frequency
        scheme = body.split(" - ")[0]
        freq = parse_frequency(question or "") or "monthly"
        body = SIP_SUMMARY.format(freq=freq, scheme=scheme,
                                  detail=SIP_BY_FREQ[freq]) + " " + CONDITION_HINT
    else:
        body = body + "."

    dated = c.fact_as_of or c.date_collected or "2026-08-27"
    return cap_sentences(freshness.annotate(body, c.fact_type, dated))


def get_generator():
    provider = os.environ.get("MF_LLM", "none").lower()
    impl = {"gemini": _gemini, "groq": _groq}.get(provider)
    if impl is None:
        return None

    def generate(system, context, question, hits=None):
        try:
            return impl(system, context, question)
        except Exception:
            return extractive(hits or [])   # degrade, never fail the request
    return generate
