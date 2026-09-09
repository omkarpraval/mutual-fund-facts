"""
LangGraph State definition for Mutual Fund Assistant.
"""
from typing import TypedDict, List, Optional, Dict, Any
from app.schemas import QueryClass


class GraphState(TypedDict, total=False):
    question: str
    selected_scheme_id: Optional[str]
    topic: Optional[str]
    topic_how: Optional[str]
    
    # Scheme matching
    scheme_id: Optional[str]
    canonical_name: Optional[str]
    matched_on: Optional[str]
    matched_text: Optional[str]
    candidates: List[str]
    conflict: Optional[str]
    
    # Guards & Refusals
    pii_kinds: List[str]
    refusal_kind: Optional[str]
    partial_refusal: Optional[str]
    known_gap: bool
    available_labels: List[str]
    
    # Retrieval & Citations
    hits: List[Any]
    citations: List[Any]
    unapproved_citations: List[Any]
    feasibility_lead: Optional[str]
    
    # Response
    query_class: QueryClass
    message: str
    debug: Dict[str, Any]
