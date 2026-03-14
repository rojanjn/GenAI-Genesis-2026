"""Embeddings module for GenAI-Genesis-2026."""

from .embedding_service import generate_embedding
from .similarity_search import cosine_similarity, find_similar_entries

__all__ = [
    "generate_embedding",
    "cosine_similarity",
    "find_similar_entries",
]
