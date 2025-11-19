"""Content filtering and safety guardrails."""

import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ContentFilter:
    """Filter inappropriate or harmful content."""

    def __init__(
        self,
        max_length: int = 4000,
        blocked_patterns: Optional[List[str]] = None,
        blocked_topics: Optional[List[str]] = None
    ):
        """
        Initialize content filter.
        
        Args:
            max_length: Maximum allowed text length
            blocked_patterns: List of regex patterns to block
            blocked_topics: List of topic keywords to block
        """
        self.max_length = max_length
        self.blocked_patterns = blocked_patterns or []
        self.blocked_topics = blocked_topics or [
            "illegal", "harmful", "violence", "hate", "explicit"
        ]
        
        # Compile regex patterns
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.blocked_patterns
        ]
        
        logger.info("ContentFilter initialized")

    def filter_input(self, text: str) -> Dict[str, Any]:
        """
        Filter input text.
        
        Args:
            text: Input text to filter
            
        Returns:
            Dictionary with filtering results
        """
        result = {
            "allowed": True,
            "filtered_text": text,
            "violations": [],
            "warnings": []
        }
        
        # Check length
        if len(text) > self.max_length:
            result["allowed"] = False
            result["violations"].append(f"Text exceeds maximum length of {self.max_length}")
            result["filtered_text"] = text[:self.max_length]
            result["warnings"].append("Text was truncated")
        
        # Check blocked patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                result["allowed"] = False
                result["violations"].append(f"Text matches blocked pattern: {pattern.pattern}")
        
        # Check blocked topics
        text_lower = text.lower()
        for topic in self.blocked_topics:
            if topic.lower() in text_lower:
                result["warnings"].append(f"Potentially sensitive topic detected: {topic}")
        
        return result

    def filter_output(self, text: str) -> Dict[str, Any]:
        """
        Filter output text.
        
        Args:
            text: Output text to filter
            
        Returns:
            Dictionary with filtering results
        """
        result = {
            "allowed": True,
            "filtered_text": text,
            "violations": [],
            "modifications": []
        }
        
        # Check for harmful content in output
        harmful_keywords = [
            "violence", "harm", "illegal", "dangerous", "weapon"
        ]
        
        text_lower = text.lower()
        for keyword in harmful_keywords:
            if keyword in text_lower:
                result["warnings"] = result.get("warnings", [])
                result["warnings"].append(f"Output contains potentially harmful keyword: {keyword}")
        
        # Ensure citations are properly formatted
        if "[" in text and "]" in text:
            citation_pattern = r'\[\d+\]'
            citations = re.findall(citation_pattern, text)
            if citations:
                result["modifications"].append(f"Found {len(citations)} citations")
        
        return result

    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text by removing potentially harmful content.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        return text


class InputValidator:
    """Validate user inputs."""

    @staticmethod
    def validate_query(query: str) -> Dict[str, Any]:
        """
        Validate user query.
        
        Args:
            query: User query
            
        Returns:
            Validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if empty
        if not query or not query.strip():
            result["valid"] = False
            result["errors"].append("Query cannot be empty")
            return result
        
        # Check length
        if len(query) < 3:
            result["valid"] = False
            result["errors"].append("Query too short (minimum 3 characters)")
        
        if len(query) > 1000:
            result["warnings"].append("Query is very long, consider making it more concise")
        
        # Check for special characters
        if re.search(r'[<>{}]', query):
            result["warnings"].append("Query contains special characters")
        
        return result

    @staticmethod
    def validate_source(source: str) -> Dict[str, Any]:
        """
        Validate document source.
        
        Args:
            source: Document source path or URL
            
        Returns:
            Validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "type": "unknown"
        }
        
        if not source:
            result["valid"] = False
            result["errors"].append("Source cannot be empty")
            return result
        
        # Detect source type
        if source.startswith(("http://", "https://")):
            result["type"] = "url"
        elif source.endswith(".pdf"):
            result["type"] = "pdf"
        elif source.endswith((".html", ".htm")):
            result["type"] = "html"
        elif source.endswith(".txt"):
            result["type"] = "text"
        else:
            result["type"] = "file"
        
        return result

