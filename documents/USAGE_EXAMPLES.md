# Document Usage Examples

This directory contains sample documents for testing the RAG system.

## 📚 Available Documents

### Technical Documentation
- `rag_system_guide.txt` - Comprehensive guide to RAG systems
- `python_best_practices.txt` - Python coding best practices
- `fastapi_development_guide.txt` - FastAPI development guide

### Sample Data
- Sample text files in `data/raw/`

## 🚀 Quick Start Examples

### Example 1: Ingest All Documents

```python
import requests

API_URL = "http://localhost:8000"

# Ingest all technical docs
docs = [
    "./documents/technical_docs/rag_system_guide.txt",
    "./documents/technical_docs/python_best_practices.txt",
    "./documents/technical_docs/fastapi_development_guide.txt",
]

for doc in docs:
    response = requests.post(f"{API_URL}/ingest", json={
        "source": doc,
        "chunk_strategy": "recursive",
        "chunk_size": 1000,
        "chunk_overlap": 200
    })
    print(f"Ingested {doc}: {response.json()}")
```

### Example 2: Query About RAG

```python
# Ask about RAG concepts
response = requests.post(f"{API_URL}/query", json={
    "question": "What are the core components of a RAG system?",
    "top_k": 5,
    "use_reranking": True,
    "return_context": True
})

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Citations: {result['citations']}")
```

### Example 3: Query About Python

```python
# Ask about Python best practices
response = requests.post(f"{API_URL}/query", json={
    "question": "What are Python best practices for error handling?",
    "top_k": 5
})

result = response.json()
print(f"Answer: {result['answer']}")
```

### Example 4: Query About FastAPI

```python
# Ask about FastAPI
response = requests.post(f"{API_URL}/query", json={
    "question": "How do I implement authentication in FastAPI?",
    "top_k": 5
})

result = response.json()
print(f"Answer: {result['answer']}")
```

### Example 5: Chat Mode

```python
# Start a conversation
chat_history = []

# First question
response = requests.post(f"{API_URL}/chat", json={
    "message": "What is RAG?",
    "chat_history": chat_history
})

result = response.json()
print(f"Answer: {result['answer']}")
chat_history = result['chat_history']

# Follow-up question
response = requests.post(f"{API_URL}/chat", json={
    "message": "How does retrieval work in RAG?",
    "chat_history": chat_history
})

result = response.json()
print(f"Answer: {result['answer']}")
```

### Example 6: Ingest Website + Documents

```python
# Combine website crawling with document ingestion

# 1. Ingest FastAPI documentation
requests.post(f"{API_URL}/ingest", json={
    "source": "https://fastapi.tiangolo.com/tutorial/",
    "crawl": True,
    "max_depth": 2
})

# 2. Ingest local documents
requests.post(f"{API_URL}/ingest", json={
    "source": "./documents/technical_docs/fastapi_development_guide.txt"
})

# 3. Query both sources
response = requests.post(f"{API_URL}/query", json={
    "question": "How do I create a POST endpoint in FastAPI?",
    "top_k": 5
})

print(response.json()['answer'])
```

## 🎯 Use Case Examples

### Use Case 1: Technical Q&A Bot

Build a technical support bot:

```python
# Ingest all technical documentation
# Then users can ask technical questions
questions = [
    "How do I handle errors in Python?",
    "What is dependency injection in FastAPI?",
    "How does MMR work in RAG?",
]

for question in questions:
    response = requests.post(f"{API_URL}/query", json={
        "question": question,
        "top_k": 5
    })
    print(f"Q: {question}")
    print(f"A: {response.json()['answer']}\n")
```

### Use Case 2: Documentation Assistant

Help developers find information quickly:

```python
# Interactive assistant
while True:
    question = input("Ask a question (or 'quit' to exit): ")
    if question.lower() == 'quit':
        break
    
    response = requests.post(f"{API_URL}/query", json={
        "question": question,
        "top_k": 5,
        "return_context": True
    })
    
    result = response.json()
    print(f"\nAnswer: {result['answer']}\n")
    
    if result['citations']:
        print("Sources:")
        for citation, data in result['citations'].items():
            print(f"  [{citation}] {data['source']}")
        print()
```

### Use Case 3: Knowledge Base Search

Search across multiple documents:

```python
# Build a knowledge base
documents = [
    "./documents/technical_docs/rag_system_guide.txt",
    "./documents/technical_docs/python_best_practices.txt",
    "./documents/technical_docs/fastapi_development_guide.txt",
]

# Ingest all
for doc in documents:
    requests.post(f"{API_URL}/ingest", json={"source": doc})

# Search function
def search_knowledge_base(query: str):
    response = requests.post(f"{API_URL}/query", json={
        "question": query,
        "top_k": 10,
        "return_context": True
    })
    return response.json()

# Try it
result = search_knowledge_base("Tell me about type hints")
print(result['answer'])
```

## 📊 Testing Retrieval Quality

```python
# Test retrieval with different settings

test_questions = [
    "What is RAG?",
    "How do I use type hints in Python?",
    "What is FastAPI?",
]

settings = [
    {"top_k": 3, "use_reranking": False},
    {"top_k": 5, "use_reranking": True},
    {"top_k": 10, "use_reranking": True},
]

for question in test_questions:
    print(f"\nQuestion: {question}")
    for setting in settings:
        response = requests.post(f"{API_URL}/query", json={
            "question": question,
            **setting
        })
        result = response.json()
        print(f"  Settings: {setting}")
        print(f"  Sources: {result['num_sources']}")
        print(f"  Citations: {result['num_citations']}")
```

## 🔍 Advanced Examples

### Custom Chunking Strategy

```python
# Try different chunking strategies
strategies = ["fixed", "recursive", "semantic"]

for strategy in strategies:
    response = requests.post(f"{API_URL}/ingest", json={
        "source": "./documents/technical_docs/rag_system_guide.txt",
        "chunk_strategy": strategy,
        "chunk_size": 1000
    })
    print(f"{strategy}: {response.json()['num_chunks']} chunks")
```

### Evaluate Responses

```python
# Evaluate response quality
response = requests.post(f"{API_URL}/query", json={
    "question": "What are the benefits of RAG?",
    "top_k": 5,
    "return_context": True
})

result = response.json()

# Evaluate
eval_response = requests.post(f"{API_URL}/evaluate", json={
    "question": result['question'],
    "answer": result['answer'],
    "contexts": [ctx['content'] for ctx in result['context']]
})

print(f"Evaluation: {eval_response.json()}")
```

## 💡 Tips

1. **Start with local documents** for testing
2. **Use specific questions** for better results
3. **Adjust top_k** based on your needs (3-10 usually works well)
4. **Enable reranking** for better quality
5. **Monitor statistics** at `/stats` endpoint

## 📝 Adding Your Own Documents

### Text Files
Simply add `.txt` files to any subdirectory

### PDFs
Add PDF files to `sample_pdfs/` directory

### From URLs
Use direct URLs in the ingest request:
```python
requests.post(f"{API_URL}/ingest", json={
    "source": "https://your-website.com/document.pdf"
})
```

## 🌐 Website Crawling Examples

```python
# Good sites for testing (respect robots.txt!)
websites = [
    "https://docs.python.org/3/tutorial/",
    "https://fastapi.tiangolo.com/",
    "https://docs.streamlit.io/",
]

for site in websites:
    requests.post(f"{API_URL}/ingest", json={
        "source": site,
        "crawl": True,
        "max_depth": 2  # Don't go too deep!
    })
```

---

**Happy testing! 🚀**

For more examples, check the `examples/` directory in the project root.

