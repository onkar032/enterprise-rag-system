# 🤖 Enterprise RAG System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, end-to-end Retrieval Augmented Generation (RAG) system built with modern AI/ML technologies. This project showcases advanced RAG techniques, clean architecture, and best practices for building enterprise-ready GenAI applications.

## ✨ Features

### 🎯 Core Capabilities
- **Multi-Source Ingestion**: PDF, HTML, websites with intelligent crawling
- **Advanced Chunking**: Recursive, semantic, and fixed-size strategies with metadata extraction
- **Embedding Generation**: SentenceTransformers (free) with optional OpenAI support
- **Vector Database**: ChromaDB with persistent storage and efficient retrieval
- **Query Enhancement**: Query rewriting with multiple strategies (rephrase, decompose, step-back)
- **Hybrid Retrieval**: MMR (Maximal Marginal Relevance) for diverse results
- **Reranking**: Cross-encoder and BM25 reranking for improved relevance
- **LLM Integration**: Ollama (local, free) and OpenAI support with streaming
- **Citation Support**: Automatic source citations in generated answers

### 🛡️ Production Features
- **Guardrails**: Content filtering and PII detection for safety
- **Evaluation**: RAGAS metrics + custom evaluation framework
- **Observability**: Structured logging, metrics collection, and distributed tracing
- **API**: RESTful FastAPI with comprehensive endpoints
- **UI**: Beautiful Streamlit interface for easy interaction
- **Containerization**: Docker and docker-compose for easy deployment

### 📊 Evaluation & Monitoring
- RAGAS metrics (faithfulness, relevancy, precision, recall)
- Custom metrics (context utilization, citation quality)
- Real-time performance monitoring
- Query latency tracking
- Error rate monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                         │
│                   (Streamlit / API Client)                    │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Guardrails  │  │ Observability│  │   Metrics    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      RAG Pipeline                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. Document Ingestion (PDF, HTML, Web)            │   │
│  │  2. Chunking & Metadata Extraction                  │   │
│  │  3. Embedding Generation (SentenceTransformers)     │   │
│  │  4. Vector Storage (ChromaDB)                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  5. Query Processing & Rewriting                    │   │
│  │  6. Hybrid Retrieval (Semantic + MMR)               │   │
│  │  7. Reranking (Cross-Encoder / BM25)               │   │
│  │  8. LLM Generation (Ollama / OpenAI)                │   │
│  │  9. Citation Extraction                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (optional, for containerized deployment)
- Ollama (for local LLM) or OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/RAG.git
cd RAG
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Install Ollama (for local LLM)**
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2
```

### Running the Application

#### Option 1: Local Development

**Start the API:**
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Start the UI (in another terminal):**
```bash
streamlit run ui/app.py
```

#### Option 2: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services:**
- API: http://localhost:8000
- UI: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Ollama: http://localhost:11434

## 📖 Usage

### 1. Ingest Documents

**Via API:**
```python
import requests

# Ingest a PDF
response = requests.post("http://localhost:8000/ingest", json={
    "source": "./documents/paper.pdf",
    "chunk_strategy": "recursive",
    "chunk_size": 1000,
    "chunk_overlap": 200
})

# Ingest a website with crawling
response = requests.post("http://localhost:8000/ingest", json={
    "source": "https://example.com",
    "crawl": True,
    "max_depth": 2
})
```

**Via UI:**
Go to "Document Ingestion" mode and enter your source.

### 2. Query the System

**Via API:**
```python
# Ask a question
response = requests.post("http://localhost:8000/query", json={
    "question": "What are the key findings of the research?",
    "top_k": 5,
    "use_reranking": True,
    "temperature": 0.7
})

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Citations: {result['citations']}")
```

**Via UI:**
Go to "Query" mode and ask your question.

### 3. Chat Mode

```python
# Start a conversation
response = requests.post("http://localhost:8000/chat", json={
    "message": "Tell me about the methodology",
    "chat_history": [],
    "top_k": 5
})
```

### 4. Evaluate Responses

```python
# Evaluate quality
response = requests.post("http://localhost:8000/evaluate", json={
    "question": "What is the main conclusion?",
    "answer": "The main conclusion is...",
    "contexts": ["Context 1", "Context 2"],
    "ground_truth": "Expected answer"
})
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_retrieval.py
```

## 📊 Monitoring & Observability

### Metrics Endpoint

```bash
# Get system metrics
curl http://localhost:8000/metrics
```

### Statistics Dashboard

```bash
# Get detailed statistics
curl http://localhost:8000/stats
```

### Logs

Logs are stored in `logs/rag_api.log` with structured JSON format.

## 🎯 Key Components

### 1. Document Ingestion (`src/ingestion/`)
- **PDFLoader**: Extract text from PDF files
- **HTMLLoader**: Parse HTML content
- **WebsiteLoader**: Crawl and scrape websites
- **DocumentLoaderFactory**: Automatic loader selection

### 2. Processing (`src/processing/`)
- **FixedSizeChunker**: Fixed-size chunks with overlap
- **SemanticChunker**: Sentence-boundary aware chunking
- **RecursiveChunker**: Hierarchical chunking
- **MetadataExtractor**: Extract keywords, entities, statistics

### 3. Embeddings (`src/embeddings/`)
- **SentenceTransformerEmbedder**: Free, local embeddings
- **OpenAIEmbedder**: Optional OpenAI embeddings
- Multiple model support

### 4. Vector Store (`src/vectorstore/`)
- **ChromaVectorStore**: Persistent vector storage
- MMR search for diversity
- Efficient similarity search

### 5. Retrieval (`src/retrieval/`)
- **QueryRewriter**: Improve query quality
- **HybridRetriever**: Multiple retrieval strategies
- **Reranker**: Cross-encoder and BM25 reranking

### 6. LLM (`src/llm/`)
- **OllamaGenerator**: Local LLM (free)
- **OpenAIGenerator**: OpenAI API
- **RAGPromptBuilder**: Optimized prompts

### 7. Evaluation (`src/evaluation/`)
- RAGAS integration
- Custom metrics
- Performance monitoring

### 8. Guardrails (`src/guardrails/`)
- Content filtering
- PII detection
- Input validation

## ⚙️ Configuration

Edit `.env` or `config/config.yaml` to customize:

```yaml
# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval
TOP_K=5
SIMILARITY_THRESHOLD=0.7

# LLM
OLLAMA_BASE_URL=http://localhost:11434

# Guardrails
ENABLE_CONTENT_FILTERING=true
ENABLE_PII_DETECTION=true
```

## 📈 Performance

### Benchmarks (M1 Mac, 16GB RAM)

| Operation | Time | Throughput |
|-----------|------|------------|
| Document Ingestion (100 pages) | ~45s | 2.2 pages/s |
| Embedding Generation (1000 chunks) | ~30s | 33 chunks/s |
| Query + Retrieval | ~500ms | - |
| End-to-end Query | ~3-5s | - |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Embeddings by [SentenceTransformers](https://www.sbert.net/)
- Vector DB by [ChromaDB](https://www.trychroma.com/)
- Evaluation with [RAGAS](https://github.com/explodinggradients/ragas)
- UI powered by [Streamlit](https://streamlit.io/)
- API framework: [FastAPI](https://fastapi.tiangolo.com/)
- Local LLM: [Ollama](https://ollama.com/)

## 📧 Contact

For questions or feedback, please open an issue or reach out to [your-email@example.com]

## 🚀 Future Enhancements

- [ ] Multi-modal support (images, tables)
- [ ] GraphRAG integration
- [ ] Fine-tuning embeddings
- [ ] Advanced caching strategies
- [ ] Multi-language support
- [ ] Agentic RAG with tool use
- [ ] Production deployment guides (AWS, GCP, Azure)

---

**⭐ If you find this project useful, please consider giving it a star!**

