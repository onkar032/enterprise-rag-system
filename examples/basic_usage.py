"""
Basic usage examples for the RAG System.

This script demonstrates common use cases and API interactions.
"""

import requests
import json
from typing import Dict, Any


# Configuration
API_BASE_URL = "http://localhost:8000"


def check_health() -> Dict[str, Any]:
    """Check if the API is healthy."""
    response = requests.get(f"{API_BASE_URL}/health")
    return response.json()


def ingest_document(source: str, **kwargs) -> Dict[str, Any]:
    """
    Ingest a document into the RAG system.
    
    Args:
        source: File path or URL
        **kwargs: Additional ingestion parameters
    """
    payload = {
        "source": source,
        "chunk_strategy": kwargs.get("chunk_strategy", "recursive"),
        "chunk_size": kwargs.get("chunk_size", 1000),
        "chunk_overlap": kwargs.get("chunk_overlap", 200),
        "crawl": kwargs.get("crawl", False),
        "max_depth": kwargs.get("max_depth", 2)
    }
    
    response = requests.post(f"{API_BASE_URL}/ingest", json=payload)
    return response.json()


def query_system(question: str, **kwargs) -> Dict[str, Any]:
    """
    Query the RAG system.
    
    Args:
        question: Question to ask
        **kwargs: Additional query parameters
    """
    payload = {
        "question": question,
        "top_k": kwargs.get("top_k", 5),
        "use_reranking": kwargs.get("use_reranking", True),
        "temperature": kwargs.get("temperature", 0.7),
        "return_context": kwargs.get("return_context", False)
    }
    
    response = requests.post(f"{API_BASE_URL}/query", json=payload)
    return response.json()


def chat_with_system(message: str, chat_history: list = None, **kwargs) -> Dict[str, Any]:
    """
    Chat with the RAG system.
    
    Args:
        message: User message
        chat_history: Previous conversation history
        **kwargs: Additional parameters
    """
    payload = {
        "message": message,
        "chat_history": chat_history or [],
        "top_k": kwargs.get("top_k", 5),
        "use_reranking": kwargs.get("use_reranking", True),
        "temperature": kwargs.get("temperature", 0.7)
    }
    
    response = requests.post(f"{API_BASE_URL}/chat", json=payload)
    return response.json()


def get_statistics() -> Dict[str, Any]:
    """Get system statistics."""
    response = requests.get(f"{API_BASE_URL}/stats")
    return response.json()


def evaluate_response(
    question: str,
    answer: str,
    contexts: list,
    ground_truth: str = None
) -> Dict[str, Any]:
    """
    Evaluate a RAG response.
    
    Args:
        question: The question
        answer: Generated answer
        contexts: Retrieved contexts
        ground_truth: Expected answer (optional)
    """
    payload = {
        "question": question,
        "answer": answer,
        "contexts": contexts,
        "ground_truth": ground_truth
    }
    
    response = requests.post(f"{API_BASE_URL}/evaluate", json=payload)
    return response.json()


def print_json(data: Dict[str, Any], title: str = None):
    """Pretty print JSON data."""
    if title:
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print('='*60)
    print(json.dumps(data, indent=2))


def main():
    """Run example usage scenarios."""
    
    print("RAG System - Basic Usage Examples")
    print("=" * 60)
    
    # 1. Check health
    print("\n1. Checking system health...")
    health = check_health()
    print(f"   Status: {health['status']}")
    print(f"   Version: {health['version']}")
    
    # 2. Ingest a document (example - update path)
    print("\n2. Ingesting a document...")
    print("   (Skipping - please provide your own document path)")
    
    # Uncomment and update path to test:
    # result = ingest_document("./documents/sample.pdf")
    # print_json(result, "Ingestion Result")
    
    # 3. Query the system
    print("\n3. Querying the system...")
    print("   (Requires documents to be ingested first)")
    
    # Uncomment to test:
    # result = query_system(
    #     "What are the main points?",
    #     top_k=5,
    #     return_context=True
    # )
    # print_json(result, "Query Result")
    # 
    # print(f"\n   Answer: {result['answer']}")
    # print(f"   Citations: {result['num_citations']}")
    # print(f"   Sources: {result['num_sources']}")
    
    # 4. Chat with the system
    print("\n4. Chat example...")
    print("   (Requires documents to be ingested first)")
    
    # Uncomment to test:
    # chat_history = []
    # 
    # # First message
    # result1 = chat_with_system(
    #     "What is the methodology?",
    #     chat_history=chat_history
    # )
    # print(f"\n   Q: What is the methodology?")
    # print(f"   A: {result1['answer']}")
    # 
    # # Second message (with history)
    # result2 = chat_with_system(
    #     "Can you elaborate on that?",
    #     chat_history=result1['chat_history']
    # )
    # print(f"\n   Q: Can you elaborate on that?")
    # print(f"   A: {result2['answer']}")
    
    # 5. Get statistics
    print("\n5. Getting system statistics...")
    try:
        stats = get_statistics()
        print_json(stats, "System Statistics")
    except Exception as e:
        print(f"   Error: {e}")
        print("   (System may not be running)")
    
    # 6. Evaluation example
    print("\n6. Evaluation example...")
    print("   (Example only - not executing)")
    
    # Example usage:
    # eval_result = evaluate_response(
    #     question="What is the main finding?",
    #     answer="The main finding is that...",
    #     contexts=[
    #         "Context 1: The research shows...",
    #         "Context 2: Analysis reveals..."
    #     ],
    #     ground_truth="The main finding is..."
    # )
    # print_json(eval_result, "Evaluation Result")
    
    print("\n" + "="*60)
    print("Examples complete!")
    print("\nNote: Uncomment specific examples in the code to test them.")
    print("Make sure documents are ingested before running queries.")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("   Make sure the API is running: python -m uvicorn api.main:app")
        print(f"   Expected URL: {API_BASE_URL}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

