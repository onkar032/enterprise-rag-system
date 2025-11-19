"""Main RAG pipeline orchestrating all components."""

import logging
from typing import List, Dict, Any, Optional

from .ingestion.loaders import Document, DocumentLoaderFactory
from .processing.chunker import ChunkerFactory, Chunk
from .processing.metadata_extractor import MetadataExtractor
from .embeddings.embedder import EmbeddingGenerator
from .vectorstore.base import VectorStore
from .retrieval.retriever import Retriever, HybridRetriever, RetrievedDocument
from .retrieval.reranker import Reranker
from .llm.generator import LLMGenerator
from .llm.prompts import RAGPromptBuilder

logger = logging.getLogger(__name__)


class RAGPipeline:
    """End-to-end RAG pipeline."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingGenerator,
        retriever: Retriever,
        llm_generator: LLMGenerator,
        reranker: Optional[Reranker] = None,
        prompt_builder: Optional[RAGPromptBuilder] = None
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            vector_store: Vector store for document storage
            embedder: Embedding generator
            retriever: Document retriever
            llm_generator: LLM generator
            reranker: Optional reranker for improving retrieval
            prompt_builder: Prompt builder for LLM
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.retriever = retriever
        self.llm_generator = llm_generator
        self.reranker = reranker
        self.prompt_builder = prompt_builder or RAGPromptBuilder()
        
        logger.info("RAG Pipeline initialized")

    def ingest_documents(
        self,
        source: str,
        chunk_strategy: str = "recursive",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **loader_kwargs
    ) -> Dict[str, Any]:
        """
        Ingest documents from source.
        
        Args:
            source: Source path or URL
            chunk_strategy: Chunking strategy (fixed, semantic, recursive)
            chunk_size: Size of chunks
            chunk_overlap: Overlap between chunks
            **loader_kwargs: Additional arguments for document loader
            
        Returns:
            Dictionary with ingestion statistics
        """
        logger.info(f"Ingesting documents from: {source}")
        
        # Load documents
        loader = DocumentLoaderFactory.get_loader(source, **loader_kwargs)
        documents = loader.load(source)
        logger.info(f"Loaded {len(documents)} documents")
        
        # Extract metadata
        metadata_extractor = MetadataExtractor()
        for doc in documents:
            doc.metadata = metadata_extractor.extract(doc)
        
        # Chunk documents
        chunker = ChunkerFactory.get_chunker(
            strategy=chunk_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = chunker.chunk(documents)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Generate embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Store in vector database
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        
        stored_ids = self.vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Stored {len(stored_ids)} chunks in vector store")
        
        return {
            "source": source,
            "num_documents": len(documents),
            "num_chunks": len(chunks),
            "num_stored": len(stored_ids)
        }

    def query(
        self,
        question: str,
        top_k: int = 5,
        use_reranking: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        return_context: bool = False
    ) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            use_reranking: Whether to use reranking
            temperature: LLM temperature
            max_tokens: Maximum tokens for LLM response
            return_context: Whether to return retrieved context
            
        Returns:
            Dictionary with answer, citations, and optionally context
        """
        logger.info(f"Processing query: {question[:100]}...")
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve(question, top_k=top_k * 2 if use_reranking else top_k)
        logger.info(f"Retrieved {len(retrieved_docs)} documents")
        
        # Rerank if enabled
        if use_reranking and self.reranker and len(retrieved_docs) > top_k:
            retrieved_docs = self.reranker.rerank(question, retrieved_docs, top_k=top_k)
            logger.info(f"Reranked to {len(retrieved_docs)} documents")
        else:
            retrieved_docs = retrieved_docs[:top_k]
        
        # Build prompt
        prompts = self.prompt_builder.build_rag_prompt(question, retrieved_docs)
        
        # Generate answer
        answer = self.llm_generator.generate(
            prompt=prompts["user"],
            system_prompt=prompts["system"],
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.info("Generated answer")
        
        # Extract citations
        result = self.prompt_builder.extract_citations(answer, retrieved_docs)
        
        # Add metadata
        result["question"] = question
        result["num_sources"] = len(retrieved_docs)
        
        # Add context if requested
        if return_context:
            result["context"] = [
                {
                    "content": doc.content,
                    "score": doc.score,
                    "source": doc.metadata.get("source", "unknown")
                }
                for doc in retrieved_docs
            ]
        
        return result

    def chat(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5,
        use_reranking: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Chat with the RAG system (with conversation history).
        
        Args:
            message: User message
            chat_history: Previous conversation history
            top_k: Number of documents to retrieve
            use_reranking: Whether to use reranking
            temperature: LLM temperature
            max_tokens: Maximum tokens for response
            
        Returns:
            Dictionary with answer and updated chat history
        """
        logger.info("Processing chat message")
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve(message, top_k=top_k * 2 if use_reranking else top_k)
        
        # Rerank if enabled
        if use_reranking and self.reranker and len(retrieved_docs) > top_k:
            retrieved_docs = self.reranker.rerank(message, retrieved_docs, top_k=top_k)
        else:
            retrieved_docs = retrieved_docs[:top_k]
        
        # Build chat prompt with history
        messages = self.prompt_builder.build_chat_prompt(
            message,
            retrieved_docs,
            chat_history
        )
        
        # Generate response
        answer = self.llm_generator.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract citations
        result = self.prompt_builder.extract_citations(answer, retrieved_docs)
        
        # Update chat history
        updated_history = chat_history or []
        updated_history.append({"role": "user", "content": message})
        updated_history.append({"role": "assistant", "content": answer})
        
        result["chat_history"] = updated_history
        result["num_sources"] = len(retrieved_docs)
        
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "vector_store": self.vector_store.get_collection_stats(),
            "embedding_dimension": self.embedder.dimension,
            "retriever_config": {
                "top_k": self.retriever.top_k,
                "similarity_threshold": self.retriever.similarity_threshold
            },
            "reranker_enabled": self.reranker is not None
        }

