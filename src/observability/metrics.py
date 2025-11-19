"""Metrics collection and monitoring."""

import logging
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and track system metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "queries": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "avg_latency": 0.0,
                "total_latency": 0.0
            },
            "ingestions": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "total_documents": 0,
                "total_chunks": 0
            },
            "retrieval": {
                "total_retrievals": 0,
                "avg_retrieval_time": 0.0,
                "avg_docs_retrieved": 0.0
            },
            "generation": {
                "total_generations": 0,
                "avg_generation_time": 0.0,
                "avg_tokens": 0.0
            },
            "errors": {
                "total": 0,
                "by_type": {}
            }
        }
        self.start_time = datetime.utcnow()
        logger.info("MetricsCollector initialized")

    @contextmanager
    def track_query(self):
        """Context manager to track query execution."""
        start_time = time.time()
        success = True
        
        try:
            yield
        except Exception as e:
            success = False
            self.record_error("query", str(e))
            raise
        finally:
            latency = time.time() - start_time
            self.record_query(latency, success)

    def record_query(self, latency: float, success: bool = True) -> None:
        """Record query metrics."""
        self.metrics["queries"]["total"] += 1
        
        if success:
            self.metrics["queries"]["successful"] += 1
        else:
            self.metrics["queries"]["failed"] += 1
        
        # Update latency
        self.metrics["queries"]["total_latency"] += latency
        self.metrics["queries"]["avg_latency"] = (
            self.metrics["queries"]["total_latency"] / self.metrics["queries"]["total"]
        )

    def record_ingestion(
        self,
        num_documents: int,
        num_chunks: int,
        success: bool = True
    ) -> None:
        """Record ingestion metrics."""
        self.metrics["ingestions"]["total"] += 1
        
        if success:
            self.metrics["ingestions"]["successful"] += 1
            self.metrics["ingestions"]["total_documents"] += num_documents
            self.metrics["ingestions"]["total_chunks"] += num_chunks
        else:
            self.metrics["ingestions"]["failed"] += 1

    def record_retrieval(self, retrieval_time: float, num_docs: int) -> None:
        """Record retrieval metrics."""
        self.metrics["retrieval"]["total_retrievals"] += 1
        
        # Update average retrieval time
        total = self.metrics["retrieval"]["total_retrievals"]
        self.metrics["retrieval"]["avg_retrieval_time"] = (
            (self.metrics["retrieval"]["avg_retrieval_time"] * (total - 1) + retrieval_time) / total
        )
        
        # Update average docs retrieved
        self.metrics["retrieval"]["avg_docs_retrieved"] = (
            (self.metrics["retrieval"]["avg_docs_retrieved"] * (total - 1) + num_docs) / total
        )

    def record_generation(self, generation_time: float, num_tokens: int = 0) -> None:
        """Record generation metrics."""
        self.metrics["generation"]["total_generations"] += 1
        
        # Update average generation time
        total = self.metrics["generation"]["total_generations"]
        self.metrics["generation"]["avg_generation_time"] = (
            (self.metrics["generation"]["avg_generation_time"] * (total - 1) + generation_time) / total
        )
        
        if num_tokens > 0:
            self.metrics["generation"]["avg_tokens"] = (
                (self.metrics["generation"]["avg_tokens"] * (total - 1) + num_tokens) / total
            )

    def record_error(self, error_type: str, error_message: str) -> None:
        """Record error metrics."""
        self.metrics["errors"]["total"] += 1
        
        if error_type not in self.metrics["errors"]["by_type"]:
            self.metrics["errors"]["by_type"][error_type] = 0
        
        self.metrics["errors"]["by_type"][error_type] += 1
        logger.error(f"Error recorded: {error_type} - {error_message}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat()
        }

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.__init__()
        logger.info("Metrics reset")


# Global metrics instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

