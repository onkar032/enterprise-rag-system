"""PII (Personally Identifiable Information) detection."""

import logging
import re
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .content_filter import ContentFilter

logger = logging.getLogger(__name__)


class PIIDetector:
    """Detect and optionally redact PII from text."""

    def __init__(
        self,
        detect_email: bool = True,
        detect_phone: bool = True,
        detect_ssn: bool = True,
        detect_credit_card: bool = True,
        auto_redact: bool = False
    ):
        """
        Initialize PII detector.
        
        Args:
            detect_email: Detect email addresses
            detect_phone: Detect phone numbers
            detect_ssn: Detect Social Security Numbers
            detect_credit_card: Detect credit card numbers
            auto_redact: Automatically redact detected PII
        """
        self.detect_email = detect_email
        self.detect_phone = detect_phone
        self.detect_ssn = detect_ssn
        self.detect_credit_card = detect_credit_card
        self.auto_redact = auto_redact
        
        # Regex patterns
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        logger.info("PIIDetector initialized")

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect PII in text.
        
        Args:
            text: Text to scan for PII
            
        Returns:
            Dictionary with detection results
        """
        result = {
            "contains_pii": False,
            "pii_types": [],
            "detections": {},
            "redacted_text": text
        }
        
        # Check for email
        if self.detect_email:
            emails = re.findall(self.patterns["email"], text)
            if emails:
                result["contains_pii"] = True
                result["pii_types"].append("email")
                result["detections"]["emails"] = emails
                if self.auto_redact:
                    text = re.sub(self.patterns["email"], "[EMAIL]", text)
        
        # Check for phone numbers
        if self.detect_phone:
            phones = re.findall(self.patterns["phone"], text)
            if phones:
                result["contains_pii"] = True
                result["pii_types"].append("phone")
                result["detections"]["phones"] = [f"({p[0]}) {p[1]}-{p[2]}" for p in phones]
                if self.auto_redact:
                    text = re.sub(self.patterns["phone"], "[PHONE]", text)
        
        # Check for SSN
        if self.detect_ssn:
            ssns = re.findall(self.patterns["ssn"], text)
            if ssns:
                result["contains_pii"] = True
                result["pii_types"].append("ssn")
                result["detections"]["ssns"] = ["XXX-XX-" + ssn.split("-")[-1] for ssn in ssns]
                if self.auto_redact:
                    text = re.sub(self.patterns["ssn"], "[SSN]", text)
        
        # Check for credit cards
        if self.detect_credit_card:
            cards = re.findall(self.patterns["credit_card"], text)
            if cards:
                result["contains_pii"] = True
                result["pii_types"].append("credit_card")
                result["detections"]["credit_cards"] = ["XXXX-XXXX-XXXX-" + card.replace(" ", "").replace("-", "")[-4:] for card in cards]
                if self.auto_redact:
                    text = re.sub(self.patterns["credit_card"], "[CREDIT_CARD]", text)
        
        result["redacted_text"] = text
        
        if result["contains_pii"]:
            logger.warning(f"PII detected: {result['pii_types']}")
        
        return result

    def redact(self, text: str) -> str:
        """
        Redact all PII from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Redacted text
        """
        result = self.detect(text)
        return result["redacted_text"]


class SafetyChecker:
    """Combined safety checker using content filter and PII detector."""

    def __init__(
        self,
        content_filter: "ContentFilter",
        pii_detector: PIIDetector
    ):
        """Initialize safety checker."""
        self.content_filter = content_filter
        self.pii_detector = pii_detector
        logger.info("SafetyChecker initialized")

    def check_input(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive safety check on input.
        
        Args:
            text: Input text to check
            
        Returns:
            Combined safety check results
        """
        result = {
            "safe": True,
            "violations": [],
            "warnings": [],
            "processed_text": text
        }
        
        # Content filtering
        content_result = self.content_filter.filter_input(text)
        if not content_result["allowed"]:
            result["safe"] = False
            result["violations"].extend(content_result["violations"])
        result["warnings"].extend(content_result.get("warnings", []))
        result["processed_text"] = content_result["filtered_text"]
        
        # PII detection
        pii_result = self.pii_detector.detect(result["processed_text"])
        if pii_result["contains_pii"]:
            result["warnings"].append(f"PII detected: {', '.join(pii_result['pii_types'])}")
            if self.pii_detector.auto_redact:
                result["processed_text"] = pii_result["redacted_text"]
        
        return result

    def check_output(self, text: str) -> Dict[str, Any]:
        """
        Perform safety check on output.
        
        Args:
            text: Output text to check
            
        Returns:
            Safety check results
        """
        result = {
            "safe": True,
            "violations": [],
            "warnings": [],
            "processed_text": text
        }
        
        # Content filtering
        content_result = self.content_filter.filter_output(text)
        result["warnings"].extend(content_result.get("warnings", []))
        
        # PII detection (should not be in output)
        pii_result = self.pii_detector.detect(text)
        if pii_result["contains_pii"]:
            result["safe"] = False
            result["violations"].append(f"Output contains PII: {', '.join(pii_result['pii_types'])}")
            if self.pii_detector.auto_redact:
                result["processed_text"] = pii_result["redacted_text"]
        
        return result

