"""FastAPI application for RAG system."""

import time
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import get_settings
from src.embeddings.embedder import SentenceTransformerEmbedder
from src.vectorstore.chroma_store import ChromaVectorStore
from src.retrieval.retriever import HybridRetriever
from src.retrieval.query_rewriter import QueryRewriter
from src.retrieval.reranker import CrossEncoderReranker, SimpleBM25Reranker
from src.llm.generator import LLMGeneratorFactory
from src.rag_pipeline import RAGPipeline
from src.observability.logger import setup_logging, get_logger
from src.observability.metrics import get_metrics_collector
from src.guardrails.content_filter import ContentFilter, InputValidator
from src.guardrails.pii_detector import PIIDetector, SafetyChecker
from src.evaluation.evaluator import RAGEvaluator

from .models import (
    QueryRequest, QueryResponse,
    ChatRequest, ChatResponse,
    IngestRequest, IngestResponse,
    EvaluateRequest,
    StatsResponse, HealthResponse, ErrorResponse
)

# Settings
settings = get_settings()

# Setup logging
setup_logging(
    log_level=settings.log_level,
    log_file="logs/rag_api.log"
)
logger = get_logger(__name__)

# Global instances
rag_pipeline = None
safety_checker = None
evaluator = None
metrics_collector = get_metrics_collector()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting RAG API...")
    await startup()
    yield
    # Shutdown
    logger.info("Shutting down RAG API...")
    await shutdown()


app = FastAPI(
    title="RAG System API",
    description="Production-grade Retrieval Augmented Generation System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def startup():
    """Initialize components on startup."""
    global rag_pipeline, safety_checker, evaluator
    
    try:
        logger.info("Initializing components...")
        
        # Initialize embedder
        embedder = SentenceTransformerEmbedder(
            model_name=settings.embedding_model,
            batch_size=32
        )
        
        # Initialize vector store
        vector_store = ChromaVectorStore(
            collection_name=settings.collection_name,
            persist_directory=settings.chroma_persist_directory
        )
        
        # Initialize query rewriter
        query_rewriter = QueryRewriter() if settings.enable_query_rewriting else None
        
        # Initialize retriever
        retriever = HybridRetriever(
            vector_store=vector_store,
            embedder=embedder,
            query_rewriter=query_rewriter,
            top_k=settings.top_k,
            similarity_threshold=settings.similarity_threshold,
            use_mmr=True
        )
        
        # Initialize reranker
        try:
            reranker = CrossEncoderReranker() if settings.enable_reranking else None
        except Exception as e:
            logger.warning(f"CrossEncoder not available, using BM25: {e}")
            reranker = SimpleBM25Reranker() if settings.enable_reranking else None
        
        # Initialize LLM generator
        # Use fallback mode (no external LLM required - perfect for free demo)
        try:
            if hasattr(settings, 'use_local_llm') and not settings.use_local_llm:
                logger.info("Using fallback generator (no external LLM)")
                llm_generator = LLMGeneratorFactory.create(provider="fallback")
            else:
                logger.info("Attempting to use Ollama...")
                llm_generator = LLMGeneratorFactory.create(
                    provider="ollama",
                    model_name="llama2",
                    base_url=settings.ollama_base_url
                )
        except Exception as e:
            logger.warning(f"Could not initialize LLM, using fallback: {e}")
            llm_generator = LLMGeneratorFactory.create(provider="fallback")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(
            vector_store=vector_store,
            embedder=embedder,
            retriever=retriever,
            llm_generator=llm_generator,
            reranker=reranker
        )
        
        # Initialize safety checker
        content_filter = ContentFilter(
            max_length=settings.max_token_length
        )
        pii_detector = PIIDetector(auto_redact=False)
        safety_checker = SafetyChecker(content_filter, pii_detector)
        
        # Initialize evaluator
        evaluator = RAGEvaluator()
        
        logger.info("All components initialized successfully")
    
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Cleanup complete")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint."""
    return HealthResponse(
        status="running",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system.
    
    Args:
        request: Query request
        
    Returns:
        Query response with answer and citations
    """
    start_time = time.time()
    
    try:
        # Validate input
        validation = InputValidator.validate_query(request.question)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["errors"])
        
        # Safety check
        safety_result = safety_checker.check_input(request.question)
        if not safety_result["safe"]:
            raise HTTPException(status_code=400, detail=safety_result["violations"])
        
        # Process query
        with metrics_collector.track_query():
            result = rag_pipeline.query(
                question=request.question,
                top_k=request.top_k,
                use_reranking=request.use_reranking,
                temperature=request.temperature,
                max_tokens=1000,
                return_context=request.return_context
            )
        
        # Safety check output
        output_safety = safety_checker.check_output(result["answer"])
        if not output_safety["safe"]:
            logger.warning(f"Output safety violations: {output_safety['violations']}")
        
        # Record metrics
        latency = time.time() - start_time
        metrics_collector.record_query(latency, success=True)
        
        return QueryResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        metrics_collector.record_error("query", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the RAG system.
    
    Args:
        request: Chat request
        
    Returns:
        Chat response with answer and updated history
    """
    try:
        # Validate input
        validation = InputValidator.validate_query(request.message)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["errors"])
        
        # Safety check
        safety_result = safety_checker.check_input(request.message)
        if not safety_result["safe"]:
            raise HTTPException(status_code=400, detail=safety_result["violations"])
        
        # Process chat
        result = rag_pipeline.chat(
            message=request.message,
            chat_history=request.chat_history,
            top_k=request.top_k,
            use_reranking=request.use_reranking,
            temperature=request.temperature
        )
        
        return ChatResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Ingest documents into the RAG system.
    
    Args:
        request: Ingestion request
        background_tasks: Background tasks for async processing
        
    Returns:
        Ingestion response with statistics
    """
    try:
        # Validate source
        validation = InputValidator.validate_source(request.source)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["errors"])
        
        # Ingest documents
        logger.info(f"Starting ingestion from {request.source}")
        
        result = rag_pipeline.ingest_documents(
            source=request.source,
            chunk_strategy=request.chunk_strategy,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            crawl=request.crawl,
            max_depth=request.max_depth
        )
        
        # Record metrics
        metrics_collector.record_ingestion(
            num_documents=result["num_documents"],
            num_chunks=result["num_chunks"],
            success=True
        )
        
        return IngestResponse(**result, status="success")
    
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        metrics_collector.record_ingestion(0, 0, success=False)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
async def evaluate(request: EvaluateRequest):
    """
    Evaluate RAG response.
    
    Args:
        request: Evaluation request
        
    Returns:
        Evaluation metrics
    """
    try:
        result = evaluator.evaluate_response(
            question=request.question,
            answer=request.answer,
            contexts=request.contexts,
            ground_truth=request.ground_truth
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get system statistics.
    
    Returns:
        System statistics and metrics
    """
    try:
        pipeline_stats = rag_pipeline.get_stats()
        metrics = metrics_collector.get_metrics()
        
        return StatsResponse(
            pipeline_stats=pipeline_stats,
            metrics=metrics
        )
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """
    Get Prometheus-compatible metrics.
    
    Returns:
        Metrics in Prometheus format
    """
    metrics = metrics_collector.get_metrics()
    
    # Format as Prometheus metrics
    lines = []
    lines.append(f"# HELP rag_queries_total Total number of queries")
    lines.append(f"# TYPE rag_queries_total counter")
    lines.append(f"rag_queries_total {metrics['queries']['total']}")
    
    lines.append(f"# HELP rag_query_latency_seconds Average query latency")
    lines.append(f"# TYPE rag_query_latency_seconds gauge")
    lines.append(f"rag_query_latency_seconds {metrics['queries']['avg_latency']}")
    
    return "\n".join(lines)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

