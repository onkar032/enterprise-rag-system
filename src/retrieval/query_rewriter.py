"""Query rewriting strategies for improved retrieval."""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class QueryRewriter:
    """Rewrite queries to improve retrieval quality."""

    def __init__(self, strategies: Optional[List[str]] = None):
        """
        Initialize query rewriter.
        
        Args:
            strategies: List of rewriting strategies to use
                       (rephrase, decompose, step_back)
        """
        self.strategies = strategies or ["rephrase", "step_back"]
        logger.info(f"QueryRewriter initialized with strategies: {self.strategies}")

    def rewrite(self, query: str, max_variants: int = 3) -> List[str]:
        """
        Rewrite query into multiple variants.
        
        Args:
            query: Original query
            max_variants: Maximum number of variants to generate
            
        Returns:
            List of query variants (including original)
        """
        variants = [query]  # Always include original query
        
        for strategy in self.strategies:
            if len(variants) >= max_variants:
                break
            
            if strategy == "rephrase":
                variant = self._rephrase(query)
                if variant and variant not in variants:
                    variants.append(variant)
            
            elif strategy == "decompose":
                subqueries = self._decompose(query)
                for subquery in subqueries:
                    if len(variants) >= max_variants:
                        break
                    if subquery not in variants:
                        variants.append(subquery)
            
            elif strategy == "step_back":
                variant = self._step_back(query)
                if variant and variant not in variants:
                    variants.append(variant)
        
        logger.debug(f"Generated {len(variants)} query variants")
        return variants[:max_variants]

    def _rephrase(self, query: str) -> str:
        """
        Rephrase the query (rule-based approach).
        
        In production, you'd use an LLM for this.
        This is a simple rule-based version.
        """
        # Simple rephrasing rules
        if query.startswith("What is"):
            return query.replace("What is", "Explain")
        elif query.startswith("How to"):
            return query.replace("How to", "What are the steps to")
        elif query.startswith("Why"):
            return query.replace("Why", "What is the reason for")
        
        # Add context keywords
        return f"Detailed information about {query}"

    def _decompose(self, query: str) -> List[str]:
        """
        Decompose complex query into simpler sub-queries.
        
        In production, you'd use an LLM for this.
        """
        subqueries = []
        
        # Look for conjunctions
        if " and " in query.lower():
            parts = query.lower().split(" and ")
            subqueries.extend(parts)
        
        if " or " in query.lower():
            parts = query.lower().split(" or ")
            subqueries.extend(parts)
        
        return [q.strip() for q in subqueries if q.strip()]

    def _step_back(self, query: str) -> str:
        """
        Create a higher-level "step back" query.
        
        This helps retrieve more general context.
        """
        # Extract key concepts and make more general
        keywords = query.split()
        
        # Remove question words
        question_words = {"what", "how", "why", "when", "where", "who", "which"}
        keywords = [w for w in keywords if w.lower() not in question_words]
        
        if keywords:
            # Create a more general query
            return f"Overview of {' '.join(keywords[:3])}"
        
        return query


class LLMQueryRewriter(QueryRewriter):
    """
    Query rewriter using LLM.
    
    This would use an actual LLM in production.
    Left as placeholder for now - can be implemented with Ollama or OpenAI.
    """

    def __init__(self, llm_client=None, strategies: Optional[List[str]] = None):
        """Initialize LLM query rewriter."""
        super().__init__(strategies)
        self.llm_client = llm_client
        logger.info("LLMQueryRewriter initialized (placeholder)")

    def _rephrase(self, query: str) -> str:
        """Rephrase using LLM."""
        if self.llm_client:
            # TODO: Implement LLM-based rephrasing
            prompt = f"Rephrase this query while keeping the same meaning: {query}"
            # return self.llm_client.generate(prompt)
            pass
        
        return super()._rephrase(query)

    def _decompose(self, query: str) -> List[str]:
        """Decompose using LLM."""
        if self.llm_client:
            # TODO: Implement LLM-based decomposition
            prompt = f"Break down this complex query into simpler sub-questions: {query}"
            # return self.llm_client.generate(prompt).split('\n')
            pass
        
        return super()._decompose(query)

