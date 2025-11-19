"""RAG evaluation using RAGAS and custom metrics."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RAGEvaluator:
    """Evaluate RAG system performance."""

    def __init__(
        self,
        metrics: Optional[List[str]] = None,
        save_results: bool = True,
        results_dir: str = "./evaluation_results"
    ):
        """
        Initialize RAG evaluator.
        
        Args:
            metrics: List of metrics to evaluate
            save_results: Whether to save evaluation results
            results_dir: Directory to save results
        """
        self.metrics = metrics or [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall"
        ]
        self.save_results = save_results
        self.results_dir = results_dir
        
        # Try to import RAGAS
        self.ragas_available = False
        try:
            from ragas import evaluate
            from ragas.metrics import (
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            )
            self.ragas_available = True
            logger.info("RAGAS library available for evaluation")
        except ImportError:
            logger.warning("RAGAS not available, using custom metrics only")
        
        logger.info(f"RAGEvaluator initialized with metrics: {self.metrics}")

    def evaluate_response(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single RAG response.
        
        Args:
            question: User question
            answer: Generated answer
            contexts: Retrieved context documents
            ground_truth: Optional ground truth answer
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating single response")
        
        results = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Custom metrics (always available)
        results.update(self._custom_metrics(question, answer, contexts, ground_truth))
        
        # RAGAS metrics (if available and ground truth provided)
        if self.ragas_available and ground_truth:
            try:
                ragas_results = self._ragas_metrics(question, answer, contexts, ground_truth)
                results.update(ragas_results)
            except Exception as e:
                logger.warning(f"RAGAS evaluation failed: {e}")
        
        return results

    def evaluate_batch(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate multiple test cases.
        
        Args:
            test_cases: List of test cases with question, answer, contexts, ground_truth
            
        Returns:
            Aggregated evaluation results
        """
        logger.info(f"Evaluating {len(test_cases)} test cases")
        
        all_results = []
        for test_case in test_cases:
            result = self.evaluate_response(
                question=test_case.get("question", ""),
                answer=test_case.get("answer", ""),
                contexts=test_case.get("contexts", []),
                ground_truth=test_case.get("ground_truth")
            )
            all_results.append(result)
        
        # Aggregate results
        aggregated = self._aggregate_results(all_results)
        
        # Save if requested
        if self.save_results:
            self._save_results(aggregated)
        
        return aggregated

    def _custom_metrics(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str]
    ) -> Dict[str, float]:
        """Calculate custom metrics."""
        metrics = {}
        
        # Answer length
        metrics["answer_length"] = len(answer.split())
        
        # Context utilization (how much of context is used)
        if contexts:
            context_text = " ".join(contexts).lower()
            answer_words = set(answer.lower().split())
            context_words = set(context_text.split())
            
            if context_words:
                overlap = len(answer_words.intersection(context_words))
                metrics["context_utilization"] = overlap / len(context_words)
            else:
                metrics["context_utilization"] = 0.0
        
        # Citation count
        import re
        citations = re.findall(r'\[\d+\]', answer)
        metrics["citation_count"] = len(citations)
        
        # Simple relevance score (keyword overlap)
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        if question_words:
            overlap = len(question_words.intersection(answer_words))
            metrics["keyword_relevance"] = overlap / len(question_words)
        
        # Ground truth similarity (if available)
        if ground_truth:
            metrics["answer_similarity"] = self._simple_similarity(answer, ground_truth)
        
        return metrics

    def _ragas_metrics(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: str
    ) -> Dict[str, float]:
        """Calculate RAGAS metrics."""
        try:
            from ragas import evaluate
            from ragas.metrics import (
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            )
            from datasets import Dataset
            
            # Prepare data for RAGAS
            data = {
                "question": [question],
                "answer": [answer],
                "contexts": [contexts],
                "ground_truth": [ground_truth]
            }
            dataset = Dataset.from_dict(data)
            
            # Evaluate
            metric_objects = []
            if "faithfulness" in self.metrics:
                metric_objects.append(faithfulness)
            if "answer_relevancy" in self.metrics:
                metric_objects.append(answer_relevancy)
            if "context_precision" in self.metrics:
                metric_objects.append(context_precision)
            if "context_recall" in self.metrics:
                metric_objects.append(context_recall)
            
            results = evaluate(dataset, metrics=metric_objects)
            
            return {k: v for k, v in results.items() if isinstance(v, (int, float))}
        
        except Exception as e:
            logger.error(f"RAGAS evaluation error: {e}")
            return {}

    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple evaluation results."""
        if not results:
            return {}
        
        # Extract numeric metrics
        numeric_metrics = {}
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    if key not in numeric_metrics:
                        numeric_metrics[key] = []
                    numeric_metrics[key].append(value)
        
        # Calculate averages
        aggregated = {
            "num_evaluations": len(results),
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {}
        }
        
        for metric, values in numeric_metrics.items():
            aggregated["metrics"][metric] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }
        
        return aggregated

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save evaluation results to file."""
        import os
        import json
        
        try:
            os.makedirs(self.results_dir, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_{timestamp}.json"
            filepath = os.path.join(self.results_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Evaluation results saved to {filepath}")
        
        except Exception as e:
            logger.error(f"Error saving results: {e}")


class PerformanceMonitor:
    """Monitor RAG system performance."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {
            "total_queries": 0,
            "total_ingestions": 0,
            "avg_retrieval_time": 0.0,
            "avg_generation_time": 0.0,
            "avg_end_to_end_time": 0.0
        }
        self.query_times = []
        
        logger.info("PerformanceMonitor initialized")

    def record_query(
        self,
        retrieval_time: float,
        generation_time: float,
        end_to_end_time: float
    ) -> None:
        """Record query performance metrics."""
        self.metrics["total_queries"] += 1
        self.query_times.append({
            "retrieval": retrieval_time,
            "generation": generation_time,
            "total": end_to_end_time
        })
        
        # Update averages
        self.metrics["avg_retrieval_time"] = sum(
            q["retrieval"] for q in self.query_times
        ) / len(self.query_times)
        
        self.metrics["avg_generation_time"] = sum(
            q["generation"] for q in self.query_times
        ) / len(self.query_times)
        
        self.metrics["avg_end_to_end_time"] = sum(
            q["total"] for q in self.query_times
        ) / len(self.query_times)

    def record_ingestion(self) -> None:
        """Record document ingestion."""
        self.metrics["total_ingestions"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics

