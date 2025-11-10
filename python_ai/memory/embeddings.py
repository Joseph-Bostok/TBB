"""
Embedding-based Semantic Similarity

This module provides text embedding functionality for semantic routing.
It uses sentence-transformers to convert text into vector representations
that capture semantic meaning.

Why embeddings for routing?
1. Semantic understanding: "I'm anxious" and "I feel worried" map to same expert
2. Better than keywords: Handles synonyms, paraphrasing, context
3. Continuous improvement: Can be fine-tuned on therapy conversations
4. Multi-intent detection: Can route to multiple experts if needed

Model Choice: all-MiniLM-L6-v2
- Fast inference (~5ms on CPU)
- Good semantic understanding
- Small memory footprint (80MB)
- Balanced accuracy for short texts
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import logging
from functools import lru_cache

from config import settings

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Singleton wrapper for sentence-transformers model

    Loads the model once and reuses it for all embeddings.
    Uses caching to avoid re-encoding the same text.
    """

    _instance = None
    _model = None

    def __new__(cls):
        """
        Singleton pattern to ensure only one model instance

        Why singleton?
        - Model loading is expensive (~1-2 seconds, 80MB RAM)
        - All requests can share the same model
        - Thread-safe in Python due to GIL
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the embedding model

        Lazy loading: Model is only loaded when first needed
        """
        if self._model is None:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            try:
                self._model = SentenceTransformer(settings.embedding_model)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

    @lru_cache(maxsize=1000)
    def encode_cached(self, text: str) -> np.ndarray:
        """
        Encode text with caching

        The @lru_cache decorator caches the last 1000 encodings.
        This is useful because:
        - Expert descriptions are encoded repeatedly
        - Common user phrases might repeat
        - Saves computation time

        Args:
            text: Text to encode

        Returns:
            numpy array of shape (embedding_dim,)
            For all-MiniLM-L6-v2: (384,)
        """
        return self._model.encode(text, convert_to_numpy=True)

    def encode(self, text: str) -> np.ndarray:
        """
        Encode text to embedding vector

        Args:
            text: Text to encode

        Returns:
            numpy array representing the semantic embedding
        """
        return self.encode_cached(text)

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Encode multiple texts efficiently

        Batch encoding is faster than encoding texts one-by-one.

        Args:
            texts: List of texts to encode

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        return self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors

    Cosine similarity measures the angle between vectors:
    - 1.0: Identical direction (perfect match)
    - 0.0: Perpendicular (no similarity)
    - -1.0: Opposite direction (rarely seen in sentence embeddings)

    Formula: similarity = (A Â* B) / (||A|| Ã-- ||B||)

    Why cosine over euclidean distance?
    - Normalization: Handles different text lengths
    - Direction matters: "very happy" and "extremely joyful" are similar
    - Standard in NLP: Works well with sentence embeddings

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        float: Similarity score between 0 and 1 (typically)

    Example:
        >>> vec1 = embedder.encode("I'm feeling anxious")
        >>> vec2 = embedder.encode("I'm worried and stressed")
        >>> similarity = cosine_similarity(vec1, vec2)
        >>> print(similarity)  # ~0.85 (high similarity)
    """
    # Dot product of vectors
    dot_product = np.dot(vec1, vec2)

    # Magnitude (L2 norm) of each vector
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    # Avoid division by zero
    if norm1 == 0 or norm2 == 0:
        return 0.0

    # Cosine similarity
    similarity = dot_product / (norm1 * norm2)

    return float(similarity)


def find_most_similar(
    query_embedding: np.ndarray,
    candidate_embeddings: Dict[str, np.ndarray],
    top_k: int = 1
) -> List[tuple]:
    """
    Find the most similar candidates to a query

    This is the core routing function: given a user message embedding,
    find which expert's description it's most similar to.

    Args:
        query_embedding: Embedding of the user's message
        candidate_embeddings: Dict mapping expert names to their embeddings
        top_k: Number of top matches to return

    Returns:
        List of (expert_name, similarity_score) tuples, sorted by score descending

    Example:
        >>> embedder = EmbeddingModel()
        >>> query = embedder.encode("I can't stop worrying about everything")
        >>> experts = {
        ...     "cbt": embedder.encode("anxiety, worry, negative thoughts"),
        ...     "mindfulness": embedder.encode("meditation, breathing, present moment"),
        ...     "motivation": embedder.encode("goals, achievement, confidence")
        ... }
        >>> results = find_most_similar(query, experts, top_k=2)
        >>> print(results)
        [('cbt', 0.82), ('mindfulness', 0.45)]
    """
    # Calculate similarity to each candidate
    similarities = []
    for name, candidate_embedding in candidate_embeddings.items():
        similarity = cosine_similarity(query_embedding, candidate_embedding)
        similarities.append((name, similarity))

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top K
    return similarities[:top_k]


# Global embedding model instance
embedder = EmbeddingModel()


def get_embedder() -> EmbeddingModel:
    """
    Get the global embedding model instance

    Used for dependency injection in other modules
    """
    return embedder
