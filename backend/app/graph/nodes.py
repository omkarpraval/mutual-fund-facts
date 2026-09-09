"""
LangGraph Nodes for Mutual Fund Assistant Workflow.
"""
from app.guards import pii, advice
from app.retrieval.normaliser import topic_of
from app.retrieval.intent import resolve_topic
from app.schemas import QueryClass
from app import prompt, citation, feasibility, mixed, coverage as cov_mod
from app.graph.state import GraphState


def pii_guard_node(state: GraphState) -> GraphState:
    question = state["question"]
    if kinds := pii.scan(question):
        return {
            "query_class": QueryClass.PII,
            "message": pii.MESSAGE,
            "pii_kinds": kinds,
            "debug": {"pii_kinds": kinds}
        }
    return {}


def advice_guard_node(state: GraphState) -> GraphState:
    question = state["question"]
    topic = topic_of(question)
    partial = None
    if kind := advice.detect(question, topic):
        fact_clause, adv_kind = mixed.analyse(question, topic_of, advice.detect)
        if fact_clause and adv_kind:
            return {
                "question": fact_clause[0],
                "topic": fact_clause[1],
                "partial_refusal": advice.refusal_message(adv_kind)
            }
        else:
            return {
                "query_class": QueryClass.ADVICE,
                "message": advice.refusal_message(kind),
                "refusal_kind": kind.value,
                "debug": {"refusal_kind": kind.value}
            }
    return {"topic": topic}


def router_node(state: GraphState, resolver, classifier=None, coverage=None) -> GraphState:
    question = state["question"]
    selected_scheme_id = state.get("selected_scheme_id")
    topic = state.get("topic")

    m = resolver.resolve(question, selected_scheme_id)
    conflict = None
    if (m.matched_on == "question_alias" and selected_scheme_id
            and m.scheme_id != selected_scheme_id):
        conflict = resolver.canonical(selected_scheme_id)

    how = "lookup"
    if topic is None:
        topic, how = resolve_topic(question, classifier)

    if m.matched_on == "ambiguous":
        return {
            "query_class": QueryClass.NEEDS_SCHEME,
            "message": "I have several SBI schemes in scope. Which one do you mean?",
            "candidates": m.candidates or [],
            "topic": topic,
            "topic_how": how,
            "conflict": conflict
        }

    if m.scheme_id is None and topic not in ("capital_gains_statement",):
        return {
            "query_class": QueryClass.NEEDS_SCHEME,
            "message": prompt.NEEDS_SCHEME,
            "topic": topic,
            "topic_how": how,
            "conflict": conflict
        }

    if topic is None and coverage:
        avail = cov_mod.available_labels(coverage, m.scheme_id)
        return {
            "query_class": QueryClass.OUT_OF_SCOPE,
            "message": f"I answer a defined set of factual questions, and this one isn't among them for {m.canonical_name}.",
            "scheme_id": m.scheme_id,
            "canonical_name": m.canonical_name,
            "conflict": conflict,
            "available_labels": avail
        }

    if coverage and cov_mod.is_known_gap(coverage, m.scheme_id, topic):
        avail = cov_mod.available_labels(coverage, m.scheme_id)
        return {
            "query_class": QueryClass.OUT_OF_SCOPE,
            "message": f"I have verified information for {m.canonical_name}, but {cov_mod.label(topic).lower()} isn't in the official sources indexed for it yet.",
            "scheme_id": m.scheme_id,
            "canonical_name": m.canonical_name,
            "conflict": conflict,
            "known_gap": True,
            "available_labels": avail
        }

    return {
        "scheme_id": m.scheme_id,
        "canonical_name": m.canonical_name,
        "matched_on": m.matched_on,
        "matched_text": m.matched_text,
        "topic": topic,
        "topic_how": how,
        "conflict": conflict
    }


def retrieval_node(state: GraphState, retriever, coverage=None) -> GraphState:
    question = state["question"]
    scheme_id = state.get("scheme_id")
    topic = state.get("topic")
    matched_on = state.get("matched_on")
    matched_text = state.get("matched_text")
    canonical_name = state.get("canonical_name")

    drop = [matched_text] if matched_on == "question_alias" and matched_text else []
    hits = retriever.search(question, scheme_id=scheme_id, topic=topic, drop_terms=drop)

    if not hits:
        avail = cov_mod.available_labels(coverage, scheme_id) if coverage else []
        return {
            "query_class": QueryClass.OUT_OF_SCOPE,
            "message": prompt.NO_EVIDENCE,
            "hits": [],
            "available_labels": avail
        }

    return {"hits": hits}


def citation_node(state: GraphState, approved_urls) -> GraphState:
    hits = state.get("hits", [])
    cits = citation.build([h.chunk for h in hits])
    if bad := citation.validate(cits, approved_urls):
        return {
            "query_class": QueryClass.OUT_OF_SCOPE,
            "message": prompt.NO_EVIDENCE,
            "citations": cits,
            "unapproved_citations": bad,
            "debug": {"unapproved_citations": bad}
        }
    return {"citations": cits}


def generation_node(state: GraphState, generator=None) -> GraphState:
    question = state["question"]
    hits = state.get("hits", [])
    cits = state.get("citations", [])
    canonical_name = state.get("canonical_name")
    topic = state.get("topic")

    lead = None
    if topic == "min_sip" and canonical_name:
        amt = feasibility.parse_amount(question)
        lead = feasibility.assess_sip(canonical_name, amt, feasibility.parse_frequency(question))

    text = (generator(prompt.SYSTEM_PROMPT, prompt.build_context(hits), question)
            if generator else "[generation pending]")

    debug = {
        "matched_on": state.get("matched_on"),
        "topic": topic,
        "topic_via": state.get("topic_how"),
        "feasibility": lead
    }

    return {
        "query_class": QueryClass.FACTUAL,
        "message": text,
        "citations": cits,
        "feasibility_lead": lead,
        "debug": debug
    }
