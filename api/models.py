"""API request and response models."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Request Models
class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    question: str = Field(..., description="User question", min_length=3)
    top_k: int = Field(default=5, description="Number of documents to retrieve", ge=1, le=20)
    use_reranking: bool = Field(default=True, description="Whether to use reranking")
    temperature: float = Field(default=0.7, description="LLM temperature", ge=0.0, le=2.0)
    return_context: bool = Field(default=False, description="Whether to return context documents")


class ChatRequest(BaseModel):
    """Request model for chat with RAG system."""
    message: str = Field(..., description="User message", min_length=3)
    chat_history: Optional[List[Dict[str, str]]] = Field(default=None, description="Chat history")
    top_k: int = Field(default=5, description="Number of documents to retrieve", ge=1, le=20)
    use_reranking: bool = Field(default=True, description="Whether to use reranking")
    temperature: float = Field(default=0.7, description="LLM temperature", ge=0.0, le=2.0)


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    source: str = Field(..., description="Document source (file path or URL)")
    chunk_strategy: str = Field(default="recursive", description="Chunking strategy")
    chunk_size: int = Field(default=1000, description="Size of chunks", ge=100, le=4000)
    chunk_overlap: int = Field(default=200, description="Overlap between chunks", ge=0, le=1000)
    crawl: bool = Field(default=False, description="Whether to crawl website (for URLs)")
    max_depth: int = Field(default=2, description="Max crawl depth", ge=1, le=5)


class EvaluateRequest(BaseModel):
    """Request model for evaluation."""
    question: str = Field(..., description="Test question")
    answer: str = Field(..., description="Generated answer")
    contexts: List[str] = Field(..., description="Retrieved contexts")
    ground_truth: Optional[str] = Field(default=None, description="Ground truth answer")


# Response Models
class QueryResponse(BaseModel):
    """Response model for query."""
    question: str
    answer: str
    citations: Dict[str, Any]
    num_citations: int
    num_sources: int
    context: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    """Response model for chat."""
    answer: str
    citations: Dict[str, Any]
    num_citations: int
    num_sources: int
    chat_history: List[Dict[str, str]]


class IngestResponse(BaseModel):
    """Response model for ingestion."""
    source: str
    num_documents: int
    num_chunks: int
    num_stored: int
    status: str = "success"


class StatsResponse(BaseModel):
    """Response model for statistics."""
    pipeline_stats: Dict[str, Any]
    metrics: Dict[str, Any]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    detail: Optional[str] = None
    timestamp: str

