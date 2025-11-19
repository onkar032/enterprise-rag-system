"""Embedding generation using various models."""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator(ABC):
    """Abstract base class for embedding generators."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Get embedding dimension."""
        pass


class SentenceTransformerEmbedder(EmbeddingGenerator):
    """Embedding generator using SentenceTransformers."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        batch_size: int = 32,
        normalize_embeddings: bool = True,
        device: Optional[str] = None
    ):
        """
        Initialize SentenceTransformer embedder.
        
        Args:
            model_name: Name of the SentenceTransformer model
            batch_size: Batch size for encoding
            normalize_embeddings: Whether to normalize embeddings
            device: Device to use (cuda/cpu). Auto-detected if None
        """
        logger.info(f"Loading embedding model: {model_name}")
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings
        self._dimension = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Model loaded on {device}, dimension: {self._dimension}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = self.embed_texts([text])
        return embeddings[0]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            # Filter out empty texts
            valid_texts = [t if t.strip() else " " for t in texts]
            
            embeddings = self.model.encode(
                valid_texts,
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=len(texts) > 10,
                convert_to_numpy=True
            )
            
            return embeddings.tolist()
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


class OpenAIEmbedder(EmbeddingGenerator):
    """Embedding generator using OpenAI API."""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        batch_size: int = 100
    ):
        """
        Initialize OpenAI embedder.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI embedding model name
            batch_size: Batch size for API calls
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.batch_size = batch_size
        
        # Get dimension by encoding a test string
        test_embedding = self.embed_text("test")
        self._dimension = len(test_embedding)
        
        logger.info(f"OpenAI embedder initialized, dimension: {self._dimension}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


class EmbedderFactory:
    """Factory to create embedding generators."""

    @staticmethod
    def create(
        provider: str = "sentence-transformers",
        **kwargs
    ) -> EmbeddingGenerator:
        """
        Create embedding generator.
        
        Args:
            provider: Embedding provider (sentence-transformers, openai)
            **kwargs: Additional arguments for the embedder
        """
        if provider == "sentence-transformers":
            return SentenceTransformerEmbedder(**kwargs)
        elif provider == "openai":
            return OpenAIEmbedder(**kwargs)
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

