"""
Dense embedding layer (D011). Local sentence-transformers, no API, no quota.

Deliberately behind a thin interface: the retriever accepts embedder=None
and runs BM25-only, which is how the whole pipeline stays testable in an
environment with no model weights. Nothing else in the codebase needs to
know whether dense retrieval is live.

Model weights download on first use, so run this once with network access
before the demo.
"""
from functools import lru_cache

MODEL_NAME = "BAAI/bge-small-en-v1.5"


class LocalEmbedder:
    def __init__(self, model_name: str = MODEL_NAME):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]):
        return self.model.encode(texts, normalize_embeddings=True,
                                 show_progress_bar=False).tolist()


@lru_cache(maxsize=1)
def get_embedder():
    """Returns None if weights are unavailable, so callers degrade to BM25."""
    try:
        return LocalEmbedder()
    except Exception:
        return None
