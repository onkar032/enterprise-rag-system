# API Documentation

Complete API reference for the RAG System.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. Future versions will include JWT-based auth.

## Endpoints

### 1. Health Check

#### GET `/health`

Check if the API is healthy and running.

**Response**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Status Codes**
- `200`: Service is healthy
- `503`: Service unavailable

---

### 2. Query

#### POST `/query`

Ask a question and get an answer based on ingested documents.

**Request Body**

```json
{
  "question": "What are the key findings?",
  "top_k": 5,
  "use_reranking": true,
  "temperature": 0.7,
  "return_context": false
}
```

**Parameters**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| question | string | Yes | - | The question to ask (min 3 chars) |
| top_k | integer | No | 5 | Number of documents to retrieve (1-20) |
| use_reranking | boolean | No | true | Whether to rerank results |
| temperature | float | No | 0.7 | LLM temperature (0.0-2.0) |
| return_context | boolean | No | false | Include retrieved context in response |

**Response**

```json
{
  "question": "What are the key findings?",
  "answer": "The key findings are... [1][2]",
  "citations": {
    "1": {
      "source": "document.pdf",
      "score": 0.89,
      "content_preview": "The research shows..."
    },
    "2": {
      "source": "paper.pdf",
      "score": 0.85,
      "content_preview": "Analysis reveals..."
    }
  },
  "num_citations": 2,
  "num_sources": 2,
  "context": [
    {
      "content": "Full context...",
      "score": 0.89,
      "source": "document.pdf"
    }
  ]
}
```

**Status Codes**
- `200`: Success
- `400`: Invalid request
- `500`: Server error

---

### 3. Chat

#### POST `/chat`

Have a conversation with the RAG system.

**Request Body**

```json
{
  "message": "Tell me more about that",
  "chat_history": [
    {
      "role": "user",
      "content": "What is the methodology?"
    },
    {
      "role": "assistant",
      "content": "The methodology involves..."
    }
  ],
  "top_k": 5,
  "use_reranking": true,
  "temperature": 0.7
}
```

**Parameters**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| message | string | Yes | - | User message |
| chat_history | array | No | [] | Previous conversation |
| top_k | integer | No | 5 | Number of documents to retrieve |
| use_reranking | boolean | No | true | Whether to rerank results |
| temperature | float | No | 0.7 | LLM temperature |

**Response**

```json
{
  "answer": "Building on the previous point...",
  "citations": {...},
  "num_citations": 2,
  "num_sources": 3,
  "chat_history": [
    {
      "role": "user",
      "content": "What is the methodology?"
    },
    {
      "role": "assistant",
      "content": "The methodology involves..."
    },
    {
      "role": "user",
      "content": "Tell me more about that"
    },
    {
      "role": "assistant",
      "content": "Building on the previous point..."
    }
  ]
}
```

**Status Codes**
- `200`: Success
- `400`: Invalid request
- `500`: Server error

---

### 4. Ingest Documents

#### POST `/ingest`

Ingest documents into the RAG system.

**Request Body**

```json
{
  "source": "./documents/paper.pdf",
  "chunk_strategy": "recursive",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "crawl": false,
  "max_depth": 2
}
```

**Parameters**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| source | string | Yes | - | File path or URL |
| chunk_strategy | string | No | "recursive" | Chunking strategy (recursive, semantic, fixed) |
| chunk_size | integer | No | 1000 | Size of chunks (100-4000) |
| chunk_overlap | integer | No | 200 | Overlap between chunks |
| crawl | boolean | No | false | Crawl website (for URLs) |
| max_depth | integer | No | 2 | Max crawl depth (1-5) |

**Response**

```json
{
  "source": "./documents/paper.pdf",
  "num_documents": 1,
  "num_chunks": 45,
  "num_stored": 45,
  "status": "success"
}
```

**Status Codes**
- `200`: Success
- `400`: Invalid source
- `500`: Ingestion error

---

### 5. Evaluate

#### POST `/evaluate`

Evaluate a RAG response.

**Request Body**

```json
{
  "question": "What is the main finding?",
  "answer": "The main finding is...",
  "contexts": [
    "Context 1...",
    "Context 2..."
  ],
  "ground_truth": "Expected answer..."
}
```

**Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| question | string | Yes | The question asked |
| answer | string | Yes | Generated answer |
| contexts | array | Yes | Retrieved contexts |
| ground_truth | string | No | Expected answer |

**Response**

```json
{
  "question": "What is the main finding?",
  "answer": "The main finding is...",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "answer_length": 45,
  "citation_count": 2,
  "context_utilization": 0.67,
  "keyword_relevance": 0.82,
  "answer_similarity": 0.91
}
```

---

### 6. Statistics

#### GET `/stats`

Get system statistics and metrics.

**Response**

```json
{
  "pipeline_stats": {
    "vector_store": {
      "collection_name": "rag_documents",
      "document_count": 150,
      "persist_directory": "./chroma_db"
    },
    "embedding_dimension": 384,
    "retriever_config": {
      "top_k": 5,
      "similarity_threshold": 0.7
    },
    "reranker_enabled": true
  },
  "metrics": {
    "queries": {
      "total": 42,
      "successful": 40,
      "failed": 2,
      "avg_latency": 2.34
    },
    "ingestions": {
      "total": 5,
      "successful": 5,
      "failed": 0,
      "total_documents": 10,
      "total_chunks": 150
    },
    "uptime_seconds": 3600
  }
}
```

---

### 7. Metrics (Prometheus)

#### GET `/metrics`

Get Prometheus-compatible metrics.

**Response** (Plain text)

```
# HELP rag_queries_total Total number of queries
# TYPE rag_queries_total counter
rag_queries_total 42

# HELP rag_query_latency_seconds Average query latency
# TYPE rag_query_latency_seconds gauge
rag_query_latency_seconds 2.34
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Request validation failed |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service is down |

---

## Rate Limiting

Current rate limits (future):
- 60 requests per minute per IP
- 1000 requests per day per API key

---

## Interactive API Docs

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Code Examples

### Python

```python
import requests

# Query the system
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "What are the main findings?",
        "top_k": 5,
        "use_reranking": True
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
```

### cURL

```bash
# Query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "top_k": 5
  }'

# Ingest
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "./documents/paper.pdf",
    "chunk_strategy": "recursive"
  }'
```

### JavaScript

```javascript
// Query the system
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What are the main findings?',
    top_k: 5
  })
});

const result = await response.json();
console.log(result.answer);
```

---

## WebSocket Support (Future)

Future versions will support WebSocket for streaming responses:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/query');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Streaming chunk:', data.chunk);
};

ws.send(JSON.stringify({
  question: 'What are the main findings?'
}));
```

---

## Versioning

API version is included in the response headers:

```
X-API-Version: 1.0.0
```

Future versions will use URL versioning:
- `/v1/query`
- `/v2/query`

