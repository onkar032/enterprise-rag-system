"""Document retrieval system."""

import logging
from typing import List, Dict, Any, Optional, Tuple

from ..embeddings.embedder import EmbeddingGenerator
from ..vectorstore.base import VectorStore
from .query_rewriter import QueryRewriter

logger = logging.getLogger(__name__)


class RetrievedDocument:
    """Container for retrieved document with metadata."""

    def __init__(
        self,
        content: str,
        score: float,
        metadata: Dict[str, Any],
        query: Optional[str] = None
    ):
        """Initialize retrieved document."""
        self.content = content
        self.score = score
        self.metadata = metadata
        self.query = query

    def __repr__(self) -> str:
        """String representation."""
        return f"RetrievedDocument(score={self.score:.3f}, source={self.metadata.get('source', 'unknown')})"


class Retriever:
    """Base retriever class."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingGenerator,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ):
        """
        Initialize retriever.
        
        Args:
            vector_store: Vector store for retrieval
            embedder: Embedding generator
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        logger.info(f"Retriever initialized with top_k={top_k}")

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query string
            top_k: Number of documents to retrieve (overrides default)
            filter: Metadata filter
            
        Returns:
            List of retrieved documents
        """
        k = top_k or self.top_k
        
        logger.info(f"Retrieving documents for query: {query[:100]}...")
        
        # Generate query embedding
        query_embedding = self.embedder.embed_text(query)
        
        # Search vector store
        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            k=k,
            filter=filter
        )
        
        # Filter by similarity threshold and convert to RetrievedDocument
        retrieved_docs = []
        for content, score, metadata in results:
            if score >= self.similarity_threshold:
                doc = RetrievedDocument(
                    content=content,
                    score=score,
                    metadata=metadata,
                    query=query
                )
                retrieved_docs.append(doc)
        
        logger.info(f"Retrieved {len(retrieved_docs)} documents")
        return retrieved_docs


class HybridRetriever(Retriever):
    """
    Hybrid retriever with query rewriting and multiple search strategies.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingGenerator,
        query_rewriter: Optional[QueryRewriter] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
        use_mmr: bool = True,
        mmr_diversity: float = 0.3
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_store: Vector store for retrieval
            embedder: Embedding generator
            query_rewriter: Query rewriter for generating variants
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
            use_mmr: Whether to use MMR for diversity
            mmr_diversity: Diversity parameter for MMR
        """
        super().__init__(vector_store, embedder, top_k, similarity_threshold)
        self.query_rewriter = query_rewriter
        self.use_mmr = use_mmr
        self.mmr_diversity = mmr_diversity
        
        logger.info("HybridRetriever initialized")

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None,
        use_query_rewriting: bool = True
    ) -> List[RetrievedDocument]:
        """
        Retrieve documents using hybrid approach.
        
        Args:
            query: Query string
            top_k: Number of documents to retrieve
            filter: Metadata filter
            use_query_rewriting: Whether to use query rewriting
            
        Returns:
            List of retrieved documents (deduplicated and ranked)
        """
        k = top_k or self.top_k
        
        # Generate query variants if query rewriter is available
        queries = [query]
        if use_query_rewriting and self.query_rewriter:
            queries = self.query_rewriter.rewrite(query, max_variants=3)
            logger.info(f"Using {len(queries)} query variants")
        
        # Retrieve documents for each query variant
        all_documents = {}  # Use dict to deduplicate by content
        
        for q in queries:
            query_embedding = self.embedder.embed_text(q)
            
            # Use MMR search if enabled
            if self.use_mmr and hasattr(self.vector_store, 'mmr_search'):
                results = self.vector_store.mmr_search(
                    query_embedding=query_embedding,
                    k=k,
                    fetch_k=k * 2,
                    lambda_mult=1.0 - self.mmr_diversity,
                    filter=filter
                )
            else:
                results = self.vector_store.similarity_search(
                    query_embedding=query_embedding,
                    k=k,
                    filter=filter
                )
            
            # Add to results (keep highest score for duplicates)
            for content, score, metadata in results:
                if score >= self.similarity_threshold:
                    if content not in all_documents or all_documents[content].score < score:
                        doc = RetrievedDocument(
                            content=content,
                            score=score,
                            metadata=metadata,
                            query=q
                        )
                        all_documents[content] = doc
        
        # Sort by score and return top k
        retrieved_docs = sorted(
            all_documents.values(),
            key=lambda x: x.score,
            reverse=True
        )[:k]
        
        logger.info(f"Retrieved {len(retrieved_docs)} unique documents")
        return retrieved_docs

