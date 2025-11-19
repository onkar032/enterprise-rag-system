"""LLM generators for answer generation."""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator

logger = logging.getLogger(__name__)


class LLMGenerator(ABC):
    """Abstract base class for LLM generators."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """Generate response from prompt."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """Generate response from chat messages."""
        pass


class OllamaGenerator(LLMGenerator):
    """LLM generator using Ollama (local models)."""

    def __init__(
        self,
        model_name: str = "llama2",
        base_url: str = "http://localhost:11434",
        timeout: int = 120
    ):
        """
        Initialize Ollama generator.
        
        Args:
            model_name: Name of the Ollama model
            base_url: Base URL for Ollama API
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.base_url = base_url
        self.timeout = timeout
        
        logger.info(f"OllamaGenerator initialized with model: {model_name}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """Generate response using Ollama."""
        import requests
        
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """Generate response using Ollama chat endpoint."""
        import requests
        
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
        
        except Exception as e:
            logger.error(f"Error with Ollama chat: {e}")
            raise


class OpenAIGenerator(LLMGenerator):
    """LLM generator using OpenAI API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        timeout: int = 60
    ):
        """
        Initialize OpenAI generator.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model name
            timeout: Request timeout in seconds
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        
        logger.info(f"OpenAIGenerator initialized with model: {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """Generate response using OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(messages, temperature, max_tokens, stream)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """Generate response using OpenAI chat completion."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # Handle streaming response
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error with OpenAI: {e}")
            raise


class FallbackGenerator(LLMGenerator):
    """
    Fallback generator that formats retrieved documents without external LLM.
    Perfect for demo/free tier usage.
    """

    def __init__(self):
        """Initialize fallback generator."""
        logger.info("FallbackGenerator initialized (no external LLM required)")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """
        Generate a formatted response from the prompt.
        Extracts context from the prompt and formats it nicely.
        """
        # Extract context sections from the prompt
        if "Context:" in prompt:
            parts = prompt.split("Context:")
            if len(parts) > 1:
                context = parts[1].split("Question:")[0].strip()
                if "Question:" in prompt:
                    question = prompt.split("Question:")[1].strip()
                else:
                    question = "No specific question provided"
                
                # Format a nice response
                response = f"Based on the provided documents, here's what I found:\n\n"
                response += f"**Relevant Information:**\n\n{context}\n\n"
                response += f"**Note:** This response is based on retrieved document excerpts. "
                response += f"For more detailed analysis, consider using an LLM provider (OpenAI, Ollama, etc.)."
                
                return response
        
        # Default response if no context found
        return "I retrieved some relevant documents, but couldn't format them properly. Please try rephrasing your question."

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """Generate response from chat messages."""
        # Extract the last user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            return self.generate(user_messages[-1].get("content", ""))
        return "No user message found."


class LLMGeneratorFactory:
    """Factory to create LLM generators."""

    @staticmethod
    def create(
        provider: str = "ollama",
        **kwargs
    ) -> LLMGenerator:
        """
        Create LLM generator.
        
        Args:
            provider: LLM provider (ollama, openai, fallback)
            **kwargs: Additional arguments
        """
        if provider == "ollama":
            return OllamaGenerator(**kwargs)
        elif provider == "openai":
            return OpenAIGenerator(**kwargs)
        elif provider == "fallback":
            return FallbackGenerator()
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

