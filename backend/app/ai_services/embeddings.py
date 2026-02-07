"""
Embedding Service for Semantic Search

Converts trading concepts and educational content into vector embeddings
for semantic similarity search.

Uses sentence-transformers for local embedding generation (no API cost).
"""
from typing import List, Optional, Dict, Any, Tuple
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Lazy-loaded model to avoid slow startup
_model = None


def _get_embedding_model():
    """
    Lazy load the sentence-transformers embedding model.

    The model is loaded only when first needed to avoid slow startup times.

    Returns:
        SentenceTransformer model instance
    """
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            from app.config.ai_config import get_ai_settings

            settings = get_ai_settings()
            logger.info(f"Loading embedding model: {settings.embedding_model_name}")
            _model = SentenceTransformer(
                settings.embedding_model_name,
                cache_folder=settings.embedding_cache_dir
            )
            logger.info("Embedding model loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using fallback embeddings.")
            _model = "fallback"
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            _model = "fallback"
    return _model


class EmbeddingService:
    """
    Service for generating and comparing text embeddings.

    Uses sentence-transformers for local embedding generation,
    enabling semantic search without external API calls.
    """

    def __init__(self):
        """Initialize the embedding service."""
        self._lesson_embeddings: Dict[str, Any] = {}
        self._concept_embeddings: Dict[str, Any] = {}
        self._topic_cache: Dict[str, List[float]] = {}

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        model = _get_embedding_model()

        if model == "fallback":
            return self._fallback_embedding(text)

        try:
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return self._fallback_embedding(text)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        model = _get_embedding_model()

        if model == "fallback":
            return [self._fallback_embedding(text) for text in texts]

        try:
            embeddings = model.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [self._fallback_embedding(text) for text in texts]

    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (-1 to 1, higher is more similar)
        """
        try:
            import numpy as np

            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))
        except ImportError:
            return self._fallback_similarity(embedding1, embedding2)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def find_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find most similar candidates to a query.

        Args:
            query: The query text
            candidates: List of candidate texts to compare
            top_k: Number of top results to return

        Returns:
            List of (candidate, similarity_score) tuples sorted by similarity
        """
        if not candidates:
            return []

        query_embedding = self.get_embedding(query)
        candidate_embeddings = self.get_embeddings(candidates)

        similarities = []
        for i, candidate_emb in enumerate(candidate_embeddings):
            sim = self.calculate_similarity(query_embedding, candidate_emb)
            similarities.append((candidates[i], sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def find_similar_topics(
        self,
        query: str,
        topic_list: List[str],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find most similar topics to a query.

        Args:
            query: User's search text or detected issue
            topic_list: List of available educational topics
            top_k: Number of top results to return

        Returns:
            List of dicts with topic and relevance score
        """
        similar = self.find_similar(query, topic_list, top_k)
        return [
            {"topic": topic, "relevance_score": round(score, 3)}
            for topic, score in similar
        ]

    def index_lessons(self, lessons: List[Dict[str, Any]]) -> None:
        """
        Index lesson content for later similarity search.

        Args:
            lessons: List of lesson dictionaries with 'id' and 'content'/'title' keys
        """
        for lesson in lessons:
            lesson_id = str(lesson.get("id", ""))
            content = lesson.get("content", "") or lesson.get("title", "") or ""
            if lesson_id and content:
                embedding = self.get_embedding(content)
                self._lesson_embeddings[lesson_id] = embedding
                logger.debug(f"Indexed lesson: {lesson_id}")

    def search_lessons(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Search indexed lessons by semantic similarity.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (lesson_id, similarity_score) tuples
        """
        if not self._lesson_embeddings:
            return []

        query_embedding = self.get_embedding(query)

        results = []
        for lesson_id, lesson_emb in self._lesson_embeddings.items():
            sim = self.calculate_similarity(query_embedding, lesson_emb)
            results.append((lesson_id, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def match_patterns_to_lessons(
        self,
        patterns: List[str],
        available_lessons: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match detected trading patterns to relevant educational lessons.

        Args:
            patterns: List of detected pattern descriptions
            available_lessons: List of lesson metadata dicts

        Returns:
            Ranked list of lessons relevant to the patterns
        """
        if not patterns or not available_lessons:
            return []

        # Combine patterns into a query
        pattern_text = " ".join(patterns)

        # Get lesson contents/titles for comparison
        lesson_contents = []
        for lesson in available_lessons:
            content = lesson.get("description", "") or lesson.get("title", "") or ""
            lesson_contents.append(content)

        if not lesson_contents:
            return []

        # Find similar lessons
        similar = self.find_similar(pattern_text, lesson_contents, top_k=5)

        # Map back to lesson objects
        content_to_lesson = {}
        for lesson in available_lessons:
            content = lesson.get("description", "") or lesson.get("title", "") or ""
            content_to_lesson[content] = lesson

        result = []
        for content, score in similar:
            if content in content_to_lesson:
                lesson = content_to_lesson[content].copy()
                lesson["relevance_score"] = round(score, 3)
                result.append(lesson)

        return result

    def _fallback_embedding(self, text: str) -> List[float]:
        """
        Generate a simple fallback embedding when model is unavailable.

        Uses character-level features as a basic embedding.
        This is NOT suitable for production semantic search.

        Args:
            text: Text to embed

        Returns:
            List of floats representing a basic embedding
        """
        import hashlib

        # Create a deterministic but simple embedding
        text_lower = text.lower()

        # Generate 64-dimensional embedding based on text features
        embedding = []

        # Character frequency features (26 dimensions for a-z)
        for char in 'abcdefghijklmnopqrstuvwxyz':
            embedding.append(text_lower.count(char) / max(len(text), 1))

        # Word count features
        words = text_lower.split()
        embedding.append(len(words) / 100)  # Normalized word count

        # Hash-based features for remaining dimensions
        hash_bytes = hashlib.md5(text.encode()).digest()
        for byte in hash_bytes[:37]:  # 37 more dimensions
            embedding.append(byte / 255)

        return embedding

    def _fallback_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate similarity without numpy.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine similarity score
        """
        if len(embedding1) != len(embedding2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the singleton embedding service instance.

    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
