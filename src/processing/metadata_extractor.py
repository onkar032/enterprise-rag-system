"""Metadata extraction from documents."""

import logging
import re
from datetime import datetime
from typing import Dict, Any, List

from ..ingestion.loaders import Document

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract and enrich metadata from documents."""

    def extract(self, document: Document) -> Dict[str, Any]:
        """Extract metadata from document."""
        metadata = document.metadata.copy()
        
        # Add extraction timestamp
        metadata["extracted_at"] = datetime.utcnow().isoformat()
        
        # Extract text statistics
        metadata.update(self._extract_text_stats(document.content))
        
        # Extract keywords
        metadata["keywords"] = self._extract_keywords(document.content)
        
        # Extract entities (simple version)
        metadata["entities"] = self._extract_entities(document.content)
        
        return metadata

    def _extract_text_stats(self, text: str) -> Dict[str, Any]:
        """Extract text statistics."""
        words = text.split()
        return {
            "char_count": len(text),
            "word_count": len(words),
            "line_count": text.count('\n') + 1,
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0
        }

    def _extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """Extract keywords from text (simple frequency-based)."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Count frequencies
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in keywords[:top_k]]

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities (simple pattern-based)."""
        entities = {
            "emails": [],
            "urls": [],
            "dates": [],
            "numbers": []
        }
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities["emails"] = re.findall(email_pattern, text)
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+'
        entities["urls"] = re.findall(url_pattern, text)
        
        # Extract dates (simple patterns)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        entities["dates"] = re.findall(date_pattern, text)
        
        # Extract numbers
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        entities["numbers"] = re.findall(number_pattern, text)[:10]  # Limit to first 10
        
        return entities

