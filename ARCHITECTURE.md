# Architecture Documentation

## System Architecture

This document provides a detailed overview of the RAG System architecture, design decisions, and implementation details.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Design](#component-design)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Design Patterns](#design-patterns)
6. [Scalability](#scalability)

## High-Level Architecture

The RAG System follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│              (Streamlit UI / API Clients)                │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  • Request Validation                                    │
│  • Authentication & Authorization (future)               │
│  • Rate Limiting                                         │
│  • Response Formatting                                   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                 Business Logic Layer                     │
│                   (RAG Pipeline)                         │
│  • Query Processing                                      │
│  • Document Processing                                   │
│  • Answer Generation                                     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│              Cross-Cutting Concerns                      │
│  • Observability (Logging, Metrics, Tracing)            │
│  • Guardrails (Safety, PII)                             │
│  • Evaluation                                            │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                   Data Layer                             │
│  • Vector Store (ChromaDB)                              │
│  • File Storage                                          │
│  • Cache (future)                                        │
└─────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Document Ingestion Pipeline

**Purpose**: Load documents from various sources and prepare them for processing.

**Components**:
- `DocumentLoader` (Abstract): Base interface for all loaders
- `PDFLoader`: Extract text from PDF files
- `HTMLLoader`: Parse HTML content
- `WebsiteLoader`: Crawl websites
- `DocumentLoaderFactory`: Factory pattern for loader creation

**Design Decisions**:
- Factory pattern for flexibility
- Abstract base class for consistency
- Metadata extraction at load time

### 2. Processing Pipeline

**Purpose**: Transform documents into searchable chunks with metadata.

**Components**:
- `DocumentChunker` (Abstract): Base chunking interface
- `RecursiveChunker`: Hierarchical chunking (default)
- `SemanticChunker`: Sentence-boundary aware
- `FixedSizeChunker`: Simple fixed-size splitting
- `MetadataExtractor`: Extract keywords, entities, statistics

**Design Decisions**:
- Multiple chunking strategies for different use cases
- Metadata enrichment for better retrieval
- Configurable chunk size and overlap

### 3. Embedding Generation

**Purpose**: Convert text to vector embeddings.

**Components**:
- `EmbeddingGenerator` (Abstract): Base interface
- `SentenceTransformerEmbedder`: Local embeddings (default)
- `OpenAIEmbedder`: Cloud-based embeddings

**Design Decisions**:
- Batch processing for efficiency
- Local-first approach (free)
- Pluggable embedder architecture

### 4. Vector Store

**Purpose**: Store and retrieve document embeddings.

**Components**:
- `VectorStore` (Abstract): Base interface
- `ChromaVectorStore`: ChromaDB implementation

**Design Decisions**:
- Persistent storage
- Efficient similarity search
- MMR support for diversity

### 5. Retrieval System

**Purpose**: Retrieve relevant documents for queries.

**Components**:
- `QueryRewriter`: Improve query quality
- `Retriever`: Basic retrieval
- `HybridRetriever`: Advanced retrieval with rewriting
- `Reranker`: Improve relevance ranking

**Design Decisions**:
- Query enhancement before retrieval
- Hybrid approach (semantic + keyword)
- Optional reranking for quality

### 6. LLM Integration

**Purpose**: Generate answers using language models.

**Components**:
- `LLMGenerator` (Abstract): Base interface
- `OllamaGenerator`: Local LLM (default)
- `OpenAIGenerator`: Cloud LLM
- `RAGPromptBuilder`: Construct prompts

**Design Decisions**:
- Local-first (Ollama) for free usage
- Structured prompts with citations
- Streaming support

### 7. Evaluation Framework

**Purpose**: Measure and improve system quality.

**Components**:
- `RAGEvaluator`: Evaluation engine
- `PerformanceMonitor`: Track metrics

**Design Decisions**:
- RAGAS integration for standard metrics
- Custom metrics for specific needs
- Continuous monitoring

### 8. Guardrails

**Purpose**: Ensure safe and appropriate responses.

**Components**:
- `ContentFilter`: Block inappropriate content
- `PIIDetector`: Detect personal information
- `SafetyChecker`: Combined safety checks

**Design Decisions**:
- Input and output filtering
- Configurable detection rules
- Non-blocking warnings

## Data Flow

### Query Flow

```
User Query
    │
    ▼
Input Validation & Safety Check
    │
    ▼
Query Rewriting
    │
    ├─> Variant 1 ──┐
    ├─> Variant 2 ──┼──> Embedding Generation
    └─> Variant 3 ──┘
                     │
                     ▼
            Vector Similarity Search
                     │
                     ▼
              Document Retrieval
                     │
                     ▼
            Optional Reranking
                     │
                     ▼
            Prompt Construction
                     │
                     ▼
            LLM Generation
                     │
                     ▼
            Citation Extraction
                     │
                     ▼
            Output Safety Check
                     │
                     ▼
            Response to User
```

### Ingestion Flow

```
Document Source
    │
    ▼
Document Loading
    │
    ▼
Metadata Extraction
    │
    ▼
Text Chunking
    │
    ▼
Embedding Generation
    │
    ▼
Vector Store Storage
    │
    ▼
Ingestion Complete
```

## Technology Stack

### Core Technologies

| Component | Technology | Reason |
|-----------|-----------|---------|
| API Framework | FastAPI | High performance, async support, auto docs |
| UI Framework | Streamlit | Rapid development, beautiful interfaces |
| Embeddings | SentenceTransformers | Free, high quality, local |
| Vector DB | ChromaDB | Simple, persistent, open-source |
| LLM | Ollama | Free, local, privacy-friendly |
| Evaluation | RAGAS | Industry standard RAG metrics |

### Supporting Technologies

| Component | Technology | Reason |
|-----------|-----------|---------|
| Web Scraping | BeautifulSoup | Robust HTML parsing |
| PDF Processing | pypdf | Reliable PDF extraction |
| Observability | Python logging | Built-in, flexible |
| Containerization | Docker | Consistent deployment |
| Orchestration | Docker Compose | Easy multi-service setup |

## Design Patterns

### 1. Factory Pattern
Used for creating loaders, embedders, chunkers, and LLM generators.

```python
embedder = EmbedderFactory.create(provider="sentence-transformers")
llm = LLMGeneratorFactory.create(provider="ollama")
```

### 2. Strategy Pattern
Used for chunking strategies and retrieval methods.

```python
chunker = ChunkerFactory.get_chunker(strategy="recursive")
```

### 3. Pipeline Pattern
RAG pipeline orchestrates multiple components.

```python
pipeline = RAGPipeline(
    vector_store, embedder, retriever, llm, reranker
)
```

### 4. Singleton Pattern
Used for metrics collector and settings.

```python
metrics = get_metrics_collector()  # Always returns same instance
```

## Scalability

### Current Limitations

1. **Single Instance**: Currently designed for single-server deployment
2. **In-Memory Processing**: Large documents processed in memory
3. **Sequential Processing**: No parallel processing yet

### Future Improvements

1. **Horizontal Scaling**:
   - Load balancer for API instances
   - Distributed vector store
   - Message queue for async processing

2. **Performance Optimization**:
   - Caching layer (Redis)
   - Batch processing
   - GPU acceleration for embeddings

3. **Storage**:
   - Object storage for documents (S3)
   - Distributed vector store (Pinecone, Weaviate)
   - Database for metadata (PostgreSQL)

## Security Considerations

### Current Implementation

1. **Input Validation**: All inputs validated
2. **Content Filtering**: Inappropriate content blocked
3. **PII Detection**: Personal information detected
4. **Error Handling**: Graceful error handling

### Future Enhancements

1. **Authentication**: JWT-based auth
2. **Authorization**: Role-based access control
3. **Rate Limiting**: Per-user rate limits
4. **Encryption**: Data encryption at rest and in transit
5. **Audit Logging**: Track all system actions

## Monitoring & Observability

### Current Implementation

1. **Structured Logging**: JSON logs with context
2. **Metrics Collection**: Query latency, error rates
3. **Health Checks**: API health endpoints
4. **Statistics Dashboard**: Real-time metrics

### Future Enhancements

1. **Distributed Tracing**: OpenTelemetry integration
2. **APM**: Application Performance Monitoring
3. **Alerting**: PagerDuty/Slack integration
4. **Dashboards**: Grafana dashboards
5. **Log Aggregation**: ELK stack

## Testing Strategy

### Current Coverage

- Unit tests for core components
- Integration tests for pipeline
- API endpoint tests

### Future Improvements

1. **Load Testing**: Locust/k6 tests
2. **E2E Tests**: Full workflow tests
3. **Performance Benchmarks**: Regular benchmarking
4. **Chaos Engineering**: Failure injection tests

## Deployment Options

### 1. Local Development
```bash
python -m uvicorn api.main:app --reload
streamlit run ui/app.py
```

### 2. Docker Compose
```bash
docker-compose up
```

### 3. Kubernetes (Future)
- Helm charts
- Auto-scaling
- Rolling updates

### 4. Cloud Platforms (Future)
- AWS: ECS/EKS
- GCP: Cloud Run/GKE
- Azure: Container Apps/AKS

## Conclusion

This architecture provides a solid foundation for a production-grade RAG system while maintaining flexibility for future enhancements. The modular design allows for easy replacement of components and scaling as needed.

