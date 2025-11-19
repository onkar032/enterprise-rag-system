# Contributing to RAG System

Thank you for your interest in contributing to the RAG System! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [How to Contribute](#how-to-contribute)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

**Our Standards:**
- Be respectful and inclusive
- Welcome diverse perspectives
- Accept constructive criticism gracefully
- Focus on what is best for the community

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a branch** for your contribution
4. **Make your changes** with clear commit messages
5. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Docker (optional)
- Ollama (for testing LLM integration)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/yourusername/RAG.git
cd RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Setup pre-commit hooks (recommended)
pip install pre-commit
pre-commit install
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list. When creating a bug report, include:

- **Clear title** describing the issue
- **Detailed description** of the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable
- **Error messages** and stack traces

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear description** of the enhancement
- **Use case** explaining why it's needed
- **Proposed solution** or implementation approach
- **Alternatives considered**

### Code Contributions

We welcome code contributions! Focus areas:

1. **New Features**
   - Multi-modal support (images, tables)
   - Additional embedding models
   - New chunking strategies
   - Advanced retrieval methods

2. **Improvements**
   - Performance optimizations
   - Better error handling
   - Enhanced logging
   - UI/UX improvements

3. **Bug Fixes**
   - Fix reported issues
   - Edge case handling
   - Error recovery

4. **Documentation**
   - Code documentation
   - Usage examples
   - Tutorials
   - API documentation

5. **Testing**
   - Unit tests
   - Integration tests
   - Performance tests

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Good: Clear variable names
embedding_dimension = 384
retrieval_results = retriever.retrieve(query)

# Good: Type hints
def embed_text(self, text: str) -> List[float]:
    """Generate embedding for text."""
    pass

# Good: Docstrings
def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
    """
    Retrieve relevant documents.
    
    Args:
        query: Search query
        top_k: Number of documents to return
        
    Returns:
        List of retrieved documents
    """
    pass
```

### Code Formatting

Use `black` for code formatting:

```bash
# Format all files
black .

# Format specific file
black src/module.py
```

### Linting

Use `flake8` for linting:

```bash
# Lint all files
flake8 .

# Lint specific file
flake8 src/module.py
```

### Type Checking

Use `mypy` for type checking:

```bash
# Type check all files
mypy src/

# Type check specific file
mypy src/module.py
```

### Import Order

Organize imports as follows:

```python
# Standard library
import os
import sys
from typing import List, Dict

# Third-party
import numpy as np
from fastapi import FastAPI

# Local
from src.embeddings import Embedder
from src.retrieval import Retriever
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_retrieval.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_retrieval.py::test_retrieve
```

### Writing Tests

```python
import pytest
from src.retrieval import Retriever

class TestRetriever:
    """Test Retriever class."""
    
    @pytest.fixture
    def retriever(self):
        """Create retriever instance."""
        return Retriever(...)
    
    def test_retrieve(self, retriever):
        """Test document retrieval."""
        results = retriever.retrieve("test query")
        assert len(results) > 0
        assert all(hasattr(r, 'content') for r in results)
    
    def test_retrieve_empty_query(self, retriever):
        """Test retrieval with empty query."""
        with pytest.raises(ValueError):
            retriever.retrieve("")
```

### Test Coverage

Aim for >80% code coverage. Check coverage report:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Documentation

### Code Documentation

- **Docstrings**: Use Google-style docstrings
- **Type hints**: Add type hints to all functions
- **Comments**: Explain complex logic, not obvious code

Example:

```python
def retrieve_and_rerank(
    self,
    query: str,
    top_k: int = 5,
    rerank_top_k: int = 10
) -> List[Document]:
    """
    Retrieve and rerank documents.
    
    First retrieves rerank_top_k documents, then reranks
    and returns the top_k most relevant ones.
    
    Args:
        query: Search query
        top_k: Number of final documents to return
        rerank_top_k: Number of documents to retrieve before reranking
        
    Returns:
        List of reranked documents
        
    Raises:
        ValueError: If top_k > rerank_top_k
        
    Example:
        >>> retriever = Retriever(...)
        >>> docs = retriever.retrieve_and_rerank("machine learning", top_k=5)
    """
    pass
```

### Documentation Updates

Update documentation when:
- Adding new features
- Changing APIs
- Fixing bugs that affect usage
- Adding examples

## Pull Request Process

### Before Submitting

1. **Update your fork**:
```bash
git remote add upstream https://github.com/original/RAG.git
git fetch upstream
git rebase upstream/main
```

2. **Run tests**:
```bash
pytest
black .
flake8 .
mypy src/
```

3. **Update documentation**:
- Update README if needed
- Update docstrings
- Add examples if applicable

4. **Create clear commits**:
```bash
git commit -m "feat: add cross-encoder reranking support"
git commit -m "fix: resolve embedding dimension mismatch"
git commit -m "docs: update API documentation"
```

### Commit Message Format

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Build process or auxiliary tool changes

Examples:
```
feat: add support for OpenAI embeddings
fix: resolve ChromaDB connection timeout
docs: add advanced usage examples
refactor: simplify retrieval pipeline
test: add tests for query rewriting
```

### Pull Request Template

When submitting a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for changes
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks**: CI/CD runs tests automatically
2. **Code review**: Maintainers review your code
3. **Feedback**: Address review comments
4. **Approval**: Once approved, your PR will be merged

### After Merge

- Delete your branch
- Pull latest changes
- Celebrate! 🎉

## Development Tips

### Running in Development Mode

```bash
# API with auto-reload
python -m uvicorn api.main:app --reload

# UI with auto-reload
streamlit run ui/app.py

# Both together
./scripts/start.sh dev
```

### Debugging

```python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use your IDE's debugger
# VSCode: Set breakpoints and press F5
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = pipeline.query("test")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues
- **Discussions**: Start a discussion for questions
- **Community**: Join our community chat (future)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Thanked in the community

Thank you for contributing to RAG System! 🚀

