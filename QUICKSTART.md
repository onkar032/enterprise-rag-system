# 🚀 Quick Start Guide

Get up and running with the RAG System in 5 minutes!

## Prerequisites

- Python 3.10+
- 4GB+ RAM
- Ollama installed (for local LLM)

## Option 1: Quick Setup (Recommended)

### 1. Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd RAG

# Run setup script
chmod +x scripts/*.sh
./scripts/setup.sh
```

This will:
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create directories
- ✅ Setup environment file
- ✅ Pull Ollama model

### 2. Configure

Edit `.env` file (optional - defaults work fine):

```bash
# Main settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
TOP_K=5
```

### 3. Start Services

```bash
# Option A: Start everything with Docker
docker-compose up

# Option B: Start in development mode
./scripts/start.sh dev

# Option C: Start services separately
# Terminal 1:
./scripts/start.sh api

# Terminal 2:
./scripts/start.sh ui
```

### 4. Access

- **UI**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Option 2: Manual Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama2
```

### 3. Setup Environment

```bash
cp .env.example .env
# Edit .env if needed
```

### 4. Start Services

```bash
# Terminal 1: Start API
python -m uvicorn api.main:app --reload

# Terminal 2: Start UI
streamlit run ui/app.py
```

## 🎯 First Steps

### 1. Ingest a Document

**Via UI:**
1. Go to http://localhost:8501
2. Select "📄 Document Ingestion" mode
3. Enter a file path or URL
4. Click "📥 Ingest"

**Via API:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "./documents/sample.pdf",
    "chunk_strategy": "recursive",
    "chunk_size": 1000
  }'
```

**Via Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/ingest",
    json={"source": "./documents/sample.pdf"}
)
print(response.json())
```

### 2. Ask Questions

**Via UI:**
1. Select "💬 Query" mode
2. Enter your question
3. Click "🔍 Search"

**Via API:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main points?",
    "top_k": 5
  }'
```

**Via Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What are the main points?"}
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Citations: {result['num_citations']}")
```

### 3. Chat Mode

**Via UI:**
1. Select "💬 Query" mode
2. Choose "Chat" option
3. Start conversation

**Via API:**
```python
import requests

# First message
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What is the methodology?",
        "chat_history": []
    }
)

result = response.json()
print(result['answer'])

# Continue conversation
response2 = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Tell me more",
        "chat_history": result['chat_history']
    }
)
```

## 📝 Example Workflow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Check health
health = requests.get(f"{BASE_URL}/health").json()
print(f"Status: {health['status']}")

# 2. Ingest document
ingest_result = requests.post(
    f"{BASE_URL}/ingest",
    json={"source": "./documents/research.pdf"}
).json()
print(f"Ingested {ingest_result['num_chunks']} chunks")

# 3. Query
query_result = requests.post(
    f"{BASE_URL}/query",
    json={
        "question": "What are the key findings?",
        "top_k": 5,
        "return_context": True
    }
).json()

print(f"\nQuestion: {query_result['question']}")
print(f"Answer: {query_result['answer']}")
print(f"Sources: {query_result['num_sources']}")

# 4. View statistics
stats = requests.get(f"{BASE_URL}/stats").json()
print(f"\nTotal queries: {stats['metrics']['queries']['total']}")
```

## 🔧 Configuration Tips

### Adjust Retrieval

```python
# More documents
"top_k": 10

# Lower similarity threshold
"similarity_threshold": 0.6

# Enable/disable reranking
"use_reranking": True
```

### Change LLM Settings

```python
# More creative
"temperature": 1.0

# More deterministic
"temperature": 0.1

# Longer responses
"max_tokens": 2000
```

### Optimize Chunking

```bash
# Smaller chunks for more precise retrieval
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Larger chunks for more context
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
```

## 🐛 Troubleshooting

### API Won't Start

```bash
# Check if port is in use
lsof -i :8000

# Try different port
uvicorn api.main:app --port 8001
```

### Ollama Connection Error

```bash
# Check Ollama is running
ollama list

# Start Ollama service
ollama serve

# Pull model if missing
ollama pull llama2
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.10+
```

### ChromaDB Issues

```bash
# Clear database
rm -rf chroma_db/

# Restart services
```

### Memory Issues

```bash
# Reduce batch size in .env
EMBEDDING_BATCH_SIZE=16

# Use smaller model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 📚 Next Steps

1. **Read the docs**: Check [README.md](README.md) for full documentation
2. **Try examples**: Run examples in `examples/` directory
3. **Explore API**: Visit http://localhost:8000/docs
4. **Customize**: Edit config files for your use case
5. **Deploy**: Use Docker Compose for production

## 🎓 Learning Path

### Beginner
1. ✅ Follow this quickstart
2. ✅ Ingest sample documents
3. ✅ Try basic queries
4. ✅ Explore the UI

### Intermediate
1. ✅ Use the Python API
2. ✅ Try different chunking strategies
3. ✅ Experiment with settings
4. ✅ Check evaluation metrics

### Advanced
1. ✅ Customize the pipeline
2. ✅ Add new components
3. ✅ Deploy with Docker
4. ✅ Monitor performance

## 💡 Tips

- **Start simple**: Use default settings first
- **Monitor logs**: Check `logs/rag_api.log` for debugging
- **Use UI**: Easier for initial exploration
- **Try examples**: Run example scripts in `examples/`
- **Read docs**: Comprehensive documentation available

## 📞 Getting Help

- **Documentation**: [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Docs**: http://localhost:8000/docs
- **Examples**: `examples/` directory
- **Issues**: Check GitHub issues

## ✅ Verification

Test your setup:

```bash
# Check API
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","version":"1.0.0","timestamp":"..."}

# Check UI
# Open http://localhost:8501 in browser
```

---

**🎉 You're ready to go! Happy querying!**

For detailed documentation, see [README.md](README.md)

