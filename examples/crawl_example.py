"""
Example script demonstrating website crawling for RAG system.

This script shows how to crawl websites and ingest them into the RAG system.
"""

import requests
import time

API_BASE = "http://localhost:8000"


def crawl_website(url: str, max_depth: int = 2, chunk_size: int = 1000):
    """
    Crawl a website and ingest it into the RAG system.
    
    Args:
        url: Website URL to crawl
        max_depth: Maximum crawl depth (1-5)
        chunk_size: Size of text chunks
    """
    print(f"\n🕷️  Crawling website: {url}")
    print(f"   Max depth: {max_depth}")
    print(f"   Chunk size: {chunk_size}")
    
    # Prepare request
    payload = {
        "source": url,
        "chunk_strategy": "recursive",
        "chunk_size": chunk_size,
        "chunk_overlap": 200,
        "crawl": True,
        "max_depth": max_depth
    }
    
    try:
        # Send ingestion request
        print("\n⏳ Starting crawl (this may take a minute)...")
        response = requests.post(f"{API_BASE}/ingest", json=payload, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        # Display results
        print("\n✅ Crawl completed successfully!")
        print(f"   Status: {result['status']}")
        print(f"   Source: {result['source']}")
        print(f"   Documents ingested: {result.get('num_documents', 'N/A')}")
        print(f"   Chunks created: {result.get('num_chunks', 'N/A')}")
        
        return result
        
    except requests.exceptions.Timeout:
        print("\n⚠️  Request timeout - the crawl might be taking too long")
        print("   Try reducing max_depth or use a smaller website")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error during crawl: {e}")
        return None


def query_crawled_content(question: str, top_k: int = 5):
    """
    Query the crawled content.
    
    Args:
        question: Question to ask
        top_k: Number of documents to retrieve
    """
    print(f"\n🔍 Asking: {question}")
    
    payload = {
        "question": question,
        "top_k": top_k,
        "temperature": 0.7,
        "use_reranking": True,
        "return_context": True
    }
    
    try:
        response = requests.post(f"{API_BASE}/query", json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        print("\n✨ Answer:")
        print(result["answer"])
        print(f"\n📊 Citations: {result.get('num_citations', 0)}")
        print(f"📚 Sources: {result.get('num_sources', 0)}")
        
        if result.get("sources"):
            print("\n📖 Sources used:")
            for i, source in enumerate(result["sources"][:3], 1):
                print(f"   {i}. {source.get('source', 'Unknown')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error during query: {e}")
        return None


def main():
    """Main example function."""
    print("🚀 RAG System - Website Crawling Example")
    print("=" * 50)
    
    # Example 1: Crawl FastAPI docs (small section)
    print("\n📚 Example 1: Crawling FastAPI Documentation")
    print("-" * 50)
    
    result = crawl_website(
        url="https://fastapi.tiangolo.com/",
        max_depth=2,
        chunk_size=1000
    )
    
    if result:
        print("\n⏳ Waiting 5 seconds for indexing...")
        time.sleep(5)
        
        # Query the crawled content
        query_crawled_content("How do I create a FastAPI endpoint?")
        
        print("\n" + "=" * 50)
        
        # Another query
        query_crawled_content("What is dependency injection in FastAPI?")
    
    print("\n" + "=" * 50)
    print("✅ Example completed!")
    print("\nTry these examples:")
    print("  - Crawl Python docs")
    print("  - Crawl your favorite blog")
    print("  - Crawl technical documentation")


if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            main()
        else:
            print("❌ API is not healthy. Please start the API first.")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Please start the API first:")
        print("   cd /path/to/RAG && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000")

