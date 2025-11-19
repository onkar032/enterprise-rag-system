# Documents Directory

This directory contains sample documents for the RAG system.

## 📁 Structure

```
documents/
├── README.md (this file)
├── sample_pdfs/          # Sample PDFs for testing
├── research_papers/      # Academic papers
├── technical_docs/       # Technical documentation
└── reports/             # Reports and analyses
```

## 📥 Adding Documents

### Option 1: Add Locally
```bash
# Copy your PDFs here
cp /path/to/your/file.pdf documents/sample_pdfs/
```

### Option 2: Use URLs
You can directly ingest from URLs without downloading:
```python
# From Google Drive
"https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"

# From ArXiv
"https://arxiv.org/pdf/2005.11401.pdf"

# From any public URL
"https://example.com/document.pdf"
```

## 🎯 Usage Examples

### Ingest Local PDF
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "./documents/sample_pdfs/your_file.pdf",
    "chunk_strategy": "recursive",
    "chunk_size": 1000
  }'
```

### Ingest from URL
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "https://arxiv.org/pdf/2005.11401.pdf",
    "chunk_strategy": "recursive"
  }'
```

### Ingest Website + PDFs
```python
import requests

# 1. Ingest website documentation
requests.post("http://localhost:8000/ingest", json={
    "source": "https://docs.python.org/3/tutorial/",
    "crawl": True,
    "max_depth": 2
})

# 2. Ingest PDF
requests.post("http://localhost:8000/ingest", json={
    "source": "./documents/sample_pdfs/python_guide.pdf"
})

# 3. Now query both sources
result = requests.post("http://localhost:8000/query", json={
    "question": "How do I use Python decorators?",
    "top_k": 5
})
```

## 📚 Recommended Free PDFs

### Research Papers (ArXiv - Free & Legal)
- RAG Paper: https://arxiv.org/pdf/2005.11401.pdf
- Attention Is All You Need: https://arxiv.org/pdf/1706.03762.pdf
- BERT Paper: https://arxiv.org/pdf/1810.04805.pdf

### Books (Free & Legal)
- Python for Everybody: https://www.py4e.com/book
- Dive Into Python 3: https://diveintopython3.net/

### Documentation
- FastAPI: Can crawl from https://fastapi.tiangolo.com/
- Streamlit: Can crawl from https://docs.streamlit.io/

## 🔒 Privacy & Legal

- Only use documents you have rights to
- Respect copyright and terms of service
- For demo purposes, use:
  - Your own documents
  - Public domain materials
  - Open-access research papers
  - Documentation with permissive licenses

## 💾 Storage Limits

**GitHub:**
- Individual file: < 100MB
- Total repo: < 1GB recommended

**Alternative Storage:**
- Google Drive: 15GB free
- Dropbox: 2GB free
- OneDrive: 5GB free

