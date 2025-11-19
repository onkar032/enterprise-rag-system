"""
Advanced usage examples for the RAG System.

This script demonstrates advanced features and customization.
"""

import sys
sys.path.append('..')

from src.embeddings.embedder import SentenceTransformerEmbedder
from src.vectorstore.chroma_store import ChromaVectorStore
from src.retrieval.retriever import HybridRetriever
from src.retrieval.query_rewriter import QueryRewriter
from src.retrieval.reranker import SimpleBM25Reranker
from src.llm.generator import OllamaGenerator
from src.rag_pipeline import RAGPipeline
from src.ingestion.loaders import DocumentLoaderFactory
from src.processing.chunker import ChunkerFactory
from src.evaluation.evaluator import RAGEvaluator
from src.guardrails.content_filter import ContentFilter
from src.guardrails.pii_detector import PIIDetector, SafetyChecker


def example_1_custom_pipeline():
    """Example 1: Build a custom RAG pipeline."""
    print("\n" + "="*60)
    print("Example 1: Custom RAG Pipeline")
    print("="*60)
    
    # Initialize components with custom settings
    embedder = SentenceTransformerEmbedder(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=32,
        normalize_embeddings=True
    )
    
    vector_store = ChromaVectorStore(
        collection_name="my_custom_collection",
        persist_directory="./custom_chroma_db"
    )
    
    query_rewriter = QueryRewriter(
        strategies=["rephrase", "step_back"]
    )
    
    retriever = HybridRetriever(
        vector_store=vector_store,
        embedder=embedder,
        query_rewriter=query_rewriter,
        top_k=10,
        similarity_threshold=0.6,
        use_mmr=True,
        mmr_diversity=0.4
    )
    
    reranker = SimpleBM25Reranker(k1=1.5, b=0.75)
    
    llm = OllamaGenerator(
        model_name="llama2",
        base_url="http://localhost:11434"
    )
    
    pipeline = RAGPipeline(
        vector_store=vector_store,
        embedder=embedder,
        retriever=retriever,
        llm_generator=llm,
        reranker=reranker
    )
    
    print("✓ Custom pipeline created")
    print(f"  Embedding dimension: {embedder.dimension}")
    print(f"  Vector store: {vector_store.collection_name}")
    print(f"  Retriever top_k: {retriever.top_k}")


def example_2_advanced_ingestion():
    """Example 2: Advanced document ingestion."""
    print("\n" + "="*60)
    print("Example 2: Advanced Document Ingestion")
    print("="*60)
    
    # Load document with custom loader
    loader = DocumentLoaderFactory.get_loader(
        "https://example.com",
        crawl=True,
        max_depth=3,
        extract_links=True
    )
    
    # Use different chunking strategies
    strategies = ["fixed", "recursive", "semantic"]
    
    for strategy in strategies:
        chunker = ChunkerFactory.get_chunker(
            strategy=strategy,
            chunk_size=800,
            chunk_overlap=150,
            min_chunk_size=100
        )
        print(f"  ✓ {strategy.capitalize()} chunker ready")


def example_3_query_enhancement():
    """Example 3: Query enhancement techniques."""
    print("\n" + "="*60)
    print("Example 3: Query Enhancement")
    print("="*60)
    
    # Query rewriting
    rewriter = QueryRewriter(
        strategies=["rephrase", "decompose", "step_back"]
    )
    
    original_query = "How does machine learning work in healthcare?"
    variants = rewriter.rewrite(original_query, max_variants=5)
    
    print(f"\n  Original: {original_query}")
    print("\n  Variants:")
    for i, variant in enumerate(variants, 1):
        print(f"    {i}. {variant}")


def example_4_evaluation_workflow():
    """Example 4: Comprehensive evaluation."""
    print("\n" + "="*60)
    print("Example 4: Evaluation Workflow")
    print("="*60)
    
    evaluator = RAGEvaluator(
        metrics=["faithfulness", "answer_relevancy"],
        save_results=True,
        results_dir="./my_eval_results"
    )
    
    # Example test cases
    test_cases = [
        {
            "question": "What is the capital of France?",
            "answer": "The capital of France is Paris. [1]",
            "contexts": ["Paris is the capital and largest city of France."],
            "ground_truth": "Paris"
        },
        {
            "question": "What is photosynthesis?",
            "answer": "Photosynthesis is the process by which plants convert light into energy. [1]",
            "contexts": ["Photosynthesis is a process used by plants to convert light energy into chemical energy."],
            "ground_truth": "Photosynthesis is the process by which plants convert light into energy."
        }
    ]
    
    # Batch evaluation
    results = evaluator.evaluate_batch(test_cases)
    
    print("\n  Evaluation Results:")
    for metric, values in results.get("metrics", {}).items():
        print(f"    {metric}: {values['mean']:.3f}")


def example_5_guardrails():
    """Example 5: Safety guardrails."""
    print("\n" + "="*60)
    print("Example 5: Safety Guardrails")
    print("="*60)
    
    # Setup guardrails
    content_filter = ContentFilter(
        max_length=4000,
        blocked_topics=["illegal", "harmful"]
    )
    
    pii_detector = PIIDetector(
        detect_email=True,
        detect_phone=True,
        auto_redact=True
    )
    
    safety_checker = SafetyChecker(content_filter, pii_detector)
    
    # Test input
    test_input = "My email is john@example.com and phone is 123-456-7890"
    
    result = safety_checker.check_input(test_input)
    
    print(f"\n  Original: {test_input}")
    print(f"  Safe: {result['safe']}")
    print(f"  Warnings: {result['warnings']}")
    print(f"  Processed: {result['processed_text']}")


def example_6_retrieval_strategies():
    """Example 6: Different retrieval strategies."""
    print("\n" + "="*60)
    print("Example 6: Retrieval Strategies")
    print("="*60)
    
    embedder = SentenceTransformerEmbedder()
    vector_store = ChromaVectorStore()
    
    # Strategy 1: Basic retrieval
    from src.retrieval.retriever import Retriever
    basic_retriever = Retriever(
        vector_store=vector_store,
        embedder=embedder,
        top_k=5,
        similarity_threshold=0.7
    )
    print("  ✓ Basic retriever ready")
    
    # Strategy 2: Hybrid with query rewriting
    query_rewriter = QueryRewriter()
    hybrid_retriever = HybridRetriever(
        vector_store=vector_store,
        embedder=embedder,
        query_rewriter=query_rewriter,
        top_k=5,
        use_mmr=True
    )
    print("  ✓ Hybrid retriever ready")
    
    # Strategy 3: With reranking
    print("  ✓ Reranking strategy available")


def example_7_monitoring():
    """Example 7: Monitoring and metrics."""
    print("\n" + "="*60)
    print("Example 7: Monitoring & Metrics")
    print("="*60)
    
    from src.observability.metrics import MetricsCollector
    from src.observability.logger import setup_logging
    
    # Setup logging
    setup_logging(
        log_level="INFO",
        log_file="./logs/custom.log",
        log_format="json"
    )
    print("  ✓ Logging configured")
    
    # Setup metrics
    metrics = MetricsCollector()
    
    # Simulate some operations
    metrics.record_query(latency=2.5, success=True)
    metrics.record_ingestion(num_documents=10, num_chunks=100, success=True)
    metrics.record_retrieval(retrieval_time=0.5, num_docs=5)
    
    # Get metrics
    current_metrics = metrics.get_metrics()
    print("\n  Current Metrics:")
    print(f"    Total queries: {current_metrics['queries']['total']}")
    print(f"    Avg latency: {current_metrics['queries']['avg_latency']:.3f}s")
    print(f"    Total ingestions: {current_metrics['ingestions']['total']}")


def main():
    """Run all advanced examples."""
    print("\n" + "="*60)
    print("RAG System - Advanced Usage Examples")
    print("="*60)
    
    try:
        example_1_custom_pipeline()
        example_2_advanced_ingestion()
        example_3_query_enhancement()
        # example_4_evaluation_workflow()  # Requires actual data
        example_5_guardrails()
        example_6_retrieval_strategies()
        example_7_monitoring()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

