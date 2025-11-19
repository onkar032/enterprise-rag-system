"""Prompt templates for RAG system."""

from typing import List, Dict, Any
from ..retrieval.retriever import RetrievedDocument


class PromptTemplate:
    """Base prompt template."""

    RAG_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context.
Always cite your sources using [1], [2], etc. format when referencing information from the context.
If the context doesn't contain enough information to answer the question, say so honestly.
Be concise and accurate in your responses."""

    RAG_USER_PROMPT = """Context:
{context}

Question: {question}

Please provide a detailed answer based on the context above. Include citations [1], [2], etc. when referencing specific information."""

    QUERY_REPHRASE_PROMPT = """Rephrase the following query to be more clear and specific, while maintaining the same meaning:

Original query: {query}

Rephrased query:"""

    QUERY_DECOMPOSE_PROMPT = """Break down the following complex query into 2-3 simpler sub-questions:

Query: {query}

Sub-questions:"""


class RAGPromptBuilder:
    """Build prompts for RAG system."""

    def __init__(
        self,
        system_prompt: str = PromptTemplate.RAG_SYSTEM_PROMPT,
        user_prompt_template: str = PromptTemplate.RAG_USER_PROMPT
    ):
        """Initialize prompt builder."""
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template

    def build_rag_prompt(
        self,
        query: str,
        documents: List[RetrievedDocument],
        include_metadata: bool = True
    ) -> Dict[str, str]:
        """
        Build RAG prompt from query and retrieved documents.
        
        Args:
            query: User query
            documents: List of retrieved documents
            include_metadata: Whether to include document metadata
            
        Returns:
            Dictionary with 'system' and 'user' prompts
        """
        # Format context from documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            if include_metadata:
                source = doc.metadata.get('source', 'unknown')
                context_parts.append(f"[{i}] (Source: {source})\n{doc.content}")
            else:
                context_parts.append(f"[{i}] {doc.content}")
        
        context = "\n\n".join(context_parts)
        
        # Build user prompt
        user_prompt = self.user_prompt_template.format(
            context=context,
            question=query
        )
        
        return {
            "system": self.system_prompt,
            "user": user_prompt
        }

    def build_chat_prompt(
        self,
        query: str,
        documents: List[RetrievedDocument],
        chat_history: List[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """
        Build chat prompt with history.
        
        Args:
            query: User query
            documents: Retrieved documents
            chat_history: Previous conversation history
            
        Returns:
            List of messages for chat completion
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add chat history
        if chat_history:
            messages.extend(chat_history)
        
        # Add current query with context
        prompts = self.build_rag_prompt(query, documents)
        messages.append({"role": "user", "content": prompts["user"]})
        
        return messages

    def extract_citations(self, answer: str, documents: List[RetrievedDocument]) -> Dict[str, Any]:
        """
        Extract citations from answer and map to source documents.
        
        Args:
            answer: Generated answer
            documents: Source documents
            
        Returns:
            Dictionary with answer and citation mappings
        """
        import re
        
        # Find all citations in format [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        citations = re.findall(citation_pattern, answer)
        
        # Map citations to documents
        citation_map = {}
        for citation in set(citations):
            idx = int(citation) - 1
            if 0 <= idx < len(documents):
                doc = documents[idx]
                citation_map[citation] = {
                    "source": doc.metadata.get('source', 'unknown'),
                    "score": doc.score,
                    "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                }
        
        return {
            "answer": answer,
            "citations": citation_map,
            "num_citations": len(set(citations))
        }

