"""Reranking module for improving retrieval results."""

import logging
from typing import List
from abc import ABC, abstractmethod

from .retriever import RetrievedDocument

logger = logging.getLogger(__name__)


class Reranker(ABC):
    """Abstract base class for rerankers."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: List[RetrievedDocument],
        top_k: int = 5
    ) -> List[RetrievedDocument]:
        """Rerank documents based on query."""
        pass


class CrossEncoderReranker(Reranker):
    """Reranker using cross-encoder model."""

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        batch_size: int = 32
    ):
        """
        Initialize cross-encoder reranker.
        
        Args:
            model_name: Name of the cross-encoder model
            batch_size: Batch size for processing
        """
        try:
            from sentence_transformers import CrossEncoder
        except ImportError:
            raise ImportError(
                "sentence-transformers required for CrossEncoderReranker"
            )
        
        logger.info(f"Loading cross-encoder model: {model_name}")
        self.model = CrossEncoder(model_name)
        self.batch_size = batch_size
        logger.info("Cross-encoder reranker initialized")

    def rerank(
        self,
        query: str,
        documents: List[RetrievedDocument],
        top_k: int = 5
    ) -> List[RetrievedDocument]:
        """
        Rerank documents using cross-encoder.
        
        Args:
            query: Query string
            documents: List of retrieved documents
            top_k: Number of documents to return
            
        Returns:
            Reranked list of documents
        """
        if not documents:
            return []
        
        logger.info(f"Reranking {len(documents)} documents")
        
        # Prepare pairs for cross-encoder
        pairs = [[query, doc.content] for doc in documents]
        
        # Get scores
        scores = self.model.predict(pairs, batch_size=self.batch_size)
        
        # Update document scores
        for doc, score in zip(documents, scores):
            doc.score = float(score)
        
        # Sort by new scores and return top k
        reranked = sorted(documents, key=lambda x: x.score, reverse=True)[:top_k]
        
        logger.info(f"Reranking complete, returning top {len(reranked)}")
        return reranked


class SimpleBM25Reranker(Reranker):
    """Simple BM25-based reranker (lightweight alternative)."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 reranker.
        
        Args:
            k1: BM25 k1 parameter
            b: BM25 b parameter
        """
        self.k1 = k1
        self.b = b
        logger.info("BM25 reranker initialized")

    def rerank(
        self,
        query: str,
        documents: List[RetrievedDocument],
        top_k: int = 5
    ) -> List[RetrievedDocument]:
        """
        Rerank documents using BM25.
        
        Args:
            query: Query string
            documents: List of retrieved documents
            top_k: Number of documents to return
            
        Returns:
            Reranked list of documents
        """
        if not documents:
            return []
        
        logger.info(f"Reranking {len(documents)} documents with BM25")
        
        # Tokenize query
        query_terms = set(query.lower().split())
        
        # Calculate BM25 scores
        doc_lengths = [len(doc.content.split()) for doc in documents]
        avg_doc_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 1
        
        for doc, doc_length in zip(documents, doc_lengths):
            score = 0.0
            doc_terms = doc.content.lower().split()
            
            for term in query_terms:
                term_freq = doc_terms.count(term)
                if term_freq > 0:
                    # Simplified BM25 (without IDF)
                    numerator = term_freq * (self.k1 + 1)
                    denominator = term_freq + self.k1 * (
                        1 - self.b + self.b * (doc_length / avg_doc_length)
                    )
                    score += numerator / denominator
            
            # Combine with original similarity score
            doc.score = 0.5 * doc.score + 0.5 * score
        
        # Sort and return top k
        reranked = sorted(documents, key=lambda x: x.score, reverse=True)[:top_k]
        
        logger.info(f"Reranking complete, returning top {len(reranked)}")
        return reranked

