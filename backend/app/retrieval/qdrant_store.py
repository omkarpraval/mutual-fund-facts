"""
Qdrant Vector Store Integration for Mutual Fund Ground Truth Corpus.
Supports embedded in-memory or on-disk collections with payload filtering.
"""
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny
)
from app.schemas import Chunk


COLLECTION_NAME = "mf_facts_chunks"


class QdrantVectorStore:
    def __init__(self, chunks: List[Chunk], embedder=None, client: Optional[QdrantClient] = None):
        self.chunks = chunks
        self.embedder = embedder
        self.client = client or QdrantClient(":memory:")
        self._init_collection()

    def _init_collection(self):
        # Determine vector dimensionality
        dim = 384  # standard default for BAAI/bge-small-en-v1.5 or all-MiniLM-L6-v2
        if self.embedder is not None and hasattr(self.embedder, "dim"):
            dim = self.embedder.dim

        # Recreate collection
        if self.client.collection_exists(COLLECTION_NAME):
            self.client.delete_collection(COLLECTION_NAME)

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

        # Index points
        vectors = None
        if self.embedder:
            vectors = self.embedder.encode([c.text for c in self.chunks])

        points = []
        for idx, c in enumerate(self.chunks):
            # If no dense embedder provided, use unit vector
            vec = vectors[idx] if vectors is not None else [0.0] * dim
            payload = {
                "chunk_id": c.chunk_id,
                "scheme_id": c.scheme_id,
                "topic": c.topic,
                "fact_type": c.fact_type.value if hasattr(c.fact_type, "value") else str(c.fact_type),
                "tier": c.tier,
                "document_id": c.document_id,
                "source_url": c.source_url,
                "source_organization": c.source_organization,
                "fact_as_of": c.fact_as_of,
                "text": c.text,
                "original_idx": idx
            }
            points.append(PointStruct(id=idx, vector=vec, payload=payload))

        self.client.upsert(collection_name=COLLECTION_NAME, points=points)

    def search_filtered(self, query: str, scheme_id: Optional[str] = None,
                        topic: Optional[str] = None, top_k: int = 10):
        """
        Execute payload-filtered vector search in Qdrant.
        """
        must_conditions = []
        if scheme_id:
            # Match specific scheme or generic (Tier 2/3) chunks where scheme_id is None
            must_conditions.append(
                FieldCondition(key="scheme_id", match=MatchAny(any=[scheme_id, None, ""]))
            )

        qdrant_filter = Filter(must=must_conditions) if must_conditions else None

        if self.embedder:
            qv = self.embedder.encode([query])[0]
            hits = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=qv,
                query_filter=qdrant_filter,
                limit=top_k
            )
            return [(h.payload["original_idx"], h.score) for h in hits]

        # If offline/BM25 mode, return all eligible candidate indices
        res = self.client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=qdrant_filter,
            limit=len(self.chunks),
            with_payload=True
        )[0]
        return [(p.payload["original_idx"], 0.0) for p in res]
