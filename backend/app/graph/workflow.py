"""
LangGraph Workflow Builder for Mutual Fund Facts Assistant.
Orchestrates StateGraph with conditional edges and state transitions.
"""
from typing import Optional
from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph import nodes
from app.schemas import QueryClass


def build_graph(resolver, retriever, approved_urls, generator=None,
                classifier=None, coverage=None):
    workflow = StateGraph(GraphState)

    # 1. Define nodes
    workflow.add_node("pii_guard", nodes.pii_guard_node)
    workflow.add_node("advice_guard", nodes.advice_guard_node)
    workflow.add_node(
        "router",
        lambda state: nodes.router_node(state, resolver, classifier, coverage)
    )
    workflow.add_node(
        "retriever",
        lambda state: nodes.retrieval_node(state, retriever, coverage)
    )
    workflow.add_node(
        "citation_validator",
        lambda state: nodes.citation_node(state, approved_urls)
    )
    workflow.add_node(
        "generator",
        lambda state: nodes.generation_node(state, generator)
    )

    # 2. Define edge conditions
    def check_pii(state: GraphState) -> str:
        if state.get("query_class") == QueryClass.PII:
            return "end"
        return "continue"

    def check_advice(state: GraphState) -> str:
        if state.get("query_class") == QueryClass.ADVICE:
            return "end"
        return "continue"

    def check_router(state: GraphState) -> str:
        if state.get("query_class") in (QueryClass.NEEDS_SCHEME, QueryClass.OUT_OF_SCOPE):
            return "end"
        return "continue"

    def check_retrieval(state: GraphState) -> str:
        if state.get("query_class") == QueryClass.OUT_OF_SCOPE:
            return "end"
        return "continue"

    def check_citation(state: GraphState) -> str:
        if state.get("query_class") == QueryClass.OUT_OF_SCOPE:
            return "end"
        return "continue"

    # 3. Add edges
    workflow.set_entry_point("pii_guard")

    workflow.add_conditional_edges(
        "pii_guard",
        check_pii,
        {"end": END, "continue": "advice_guard"}
    )

    workflow.add_conditional_edges(
        "advice_guard",
        check_advice,
        {"end": END, "continue": "router"}
    )

    workflow.add_conditional_edges(
        "router",
        check_router,
        {"end": END, "continue": "retriever"}
    )

    workflow.add_conditional_edges(
        "retriever",
        check_retrieval,
        {"end": END, "continue": "citation_validator"}
    )

    workflow.add_conditional_edges(
        "citation_validator",
        check_citation,
        {"end": END, "continue": "generator"}
    )

    workflow.add_edge("generator", END)

    return workflow.compile()
