"""Document chunking strategies."""

import logging
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from ..ingestion.loaders import Document

logger = logging.getLogger(__name__)


class Chunk:
    """Chunk class to store chunk content and metadata."""

    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_id: Optional[str] = None
    ):
        """Initialize chunk."""
        self.content = content
        self.metadata = metadata or {}
        self.chunk_id = chunk_id

    def __repr__(self) -> str:
        """String representation."""
        return f"Chunk(id={self.chunk_id}, length={len(self.content)})"


class DocumentChunker(ABC):
    """Abstract base class for document chunkers."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """Initialize chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    @abstractmethod
    def chunk(self, documents: List[Document]) -> List[Chunk]:
        """Chunk documents."""
        pass

    def _create_chunk(
        self,
        content: str,
        doc_metadata: Dict[str, Any],
        chunk_index: int
    ) -> Chunk:
        """Create a chunk with metadata."""
        chunk_metadata = {
            **doc_metadata,
            "chunk_index": chunk_index,
            "chunk_size": len(content)
        }
        chunk_id = f"{doc_metadata.get('source', 'unknown')}_{chunk_index}"
        return Chunk(content=content, metadata=chunk_metadata, chunk_id=chunk_id)


class FixedSizeChunker(DocumentChunker):
    """Fixed size chunking strategy."""

    def chunk(self, documents: List[Document]) -> List[Chunk]:
        """Chunk documents using fixed size."""
        all_chunks = []
        
        for doc in documents:
            chunks = self._chunk_text(doc.content, doc.metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks

    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Chunk text into fixed-size chunks with overlap."""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_content = text[start:end]
            
            if len(chunk_content) >= self.min_chunk_size:
                chunks.append(self._create_chunk(chunk_content, metadata, chunk_index))
                chunk_index += 1
            
            start += self.chunk_size - self.chunk_overlap
            
            # Avoid infinite loop
            if self.chunk_overlap >= self.chunk_size:
                start = end
        
        return chunks


class RecursiveChunker(DocumentChunker):
    """Recursive chunking strategy that respects text structure."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
        separators: Optional[List[str]] = None
    ):
        """Initialize recursive chunker."""
        super().__init__(chunk_size, chunk_overlap, min_chunk_size)
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, documents: List[Document]) -> List[Chunk]:
        """Chunk documents recursively."""
        all_chunks = []
        
        for doc in documents:
            chunks = self._chunk_text_recursive(doc.content, doc.metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks

    def _chunk_text_recursive(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunk_index: int = 0
    ) -> List[Chunk]:
        """Recursively chunk text using separators."""
        chunks = []
        
        if len(text) <= self.chunk_size:
            if len(text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(text, metadata, chunk_index))
            return chunks

        # Try to split by separators
        for separator in self.separators:
            if separator in text:
                splits = text.split(separator)
                current_chunk = ""
                
                for split in splits:
                    if len(current_chunk) + len(split) + len(separator) <= self.chunk_size:
                        current_chunk += split + separator
                    else:
                        if len(current_chunk) >= self.min_chunk_size:
                            chunks.append(
                                self._create_chunk(current_chunk.strip(), metadata, len(chunks))
                            )
                        current_chunk = split + separator
                
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(
                        self._create_chunk(current_chunk.strip(), metadata, len(chunks))
                    )
                
                if chunks:
                    return chunks

        # Fallback to fixed size
        return FixedSizeChunker(
            self.chunk_size,
            self.chunk_overlap,
            self.min_chunk_size
        )._chunk_text(text, metadata)


class SemanticChunker(DocumentChunker):
    """Semantic chunking based on sentence boundaries and meaning."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """Initialize semantic chunker."""
        super().__init__(chunk_size, chunk_overlap, min_chunk_size)

    def chunk(self, documents: List[Document]) -> List[Chunk]:
        """Chunk documents semantically."""
        all_chunks = []
        
        for doc in documents:
            chunks = self._chunk_text_semantic(doc.content, doc.metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks

    def _chunk_text_semantic(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """Chunk text based on semantic boundaries (sentences/paragraphs)."""
        # Split into sentences
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_sentences = []
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
                current_sentences.append(sentence)
            else:
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(
                        self._create_chunk(current_chunk.strip(), metadata, len(chunks))
                    )
                
                # Add overlap
                overlap_text = " ".join(current_sentences[-2:]) if len(current_sentences) >= 2 else ""
                current_chunk = overlap_text + " " + sentence + " "
                current_sentences = current_sentences[-2:] + [sentence]
        
        if len(current_chunk) >= self.min_chunk_size:
            chunks.append(
                self._create_chunk(current_chunk.strip(), metadata, len(chunks))
            )
        
        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]


class ChunkerFactory:
    """Factory to create chunkers."""

    @staticmethod
    def get_chunker(
        strategy: str = "recursive",
        **kwargs
    ) -> DocumentChunker:
        """Get chunker based on strategy."""
        if strategy == "fixed":
            return FixedSizeChunker(**kwargs)
        elif strategy == "semantic":
            return SemanticChunker(**kwargs)
        elif strategy == "recursive":
            return RecursiveChunker(**kwargs)
        else:
            logger.warning(f"Unknown strategy {strategy}, using recursive")
            return RecursiveChunker(**kwargs)

