"""ChromaDB vector store implementation."""

import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple

import chromadb
from chromadb.config import Settings

from .base import VectorStore

logger = logging.getLogger(__name__)


class ChromaVectorStore(VectorStore):
    """Vector store implementation using ChromaDB."""

    def __init__(
        self,
        collection_name: str = "rag_documents",
        persist_directory: str = "./chroma_db",
        embedding_dimension: Optional[int] = None
    ):
        """
        Initialize ChromaDB vector store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
            embedding_dimension: Dimension of embeddings (optional)
        """
        logger.info(f"Initializing ChromaDB at {persist_directory}")
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {collection_name}")

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to the vector store."""
        try:
            if not texts or not embeddings:
                logger.warning("No texts or embeddings provided")
                return []
            
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in texts]
            
            # Prepare metadatas
            if metadatas is None:
                metadatas = [{} for _ in texts]
            
            # Convert metadata values to strings (ChromaDB requirement)
            processed_metadatas = []
            for i, metadata in enumerate(metadatas):
                processed = {}
                for key, value in metadata.items():
                    if isinstance(value, (list, dict)):
                        processed[key] = str(value)
                    elif value is None:
                        processed[key] = ""
                    else:
                        processed[key] = str(value)
                # Store the ChromaDB ID in metadata for later retrieval
                processed['chroma_id'] = ids[i]
                processed_metadatas.append(processed)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=processed_metadatas
            )
            
            logger.info(f"Added {len(texts)} documents to collection")
            return ids
        
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar documents."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Parse results
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            # Convert distances to similarity scores (1 - distance for cosine)
            similarities = [1 - dist for dist in distances]
            
            search_results = [
                (doc, score, meta)
                for doc, score, meta in zip(documents, similarities, metadatas)
            ]
            
            logger.info(f"Retrieved {len(search_results)} results")
            return search_results
        
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def delete(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    def clear(self) -> bool:
        """Clear all documents from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

    def mmr_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Maximal Marginal Relevance search for diverse results.
        
        Args:
            query_embedding: Query embedding
            k: Number of documents to return
            fetch_k: Number of documents to fetch initially
            lambda_mult: Diversity parameter (0=max diversity, 1=max relevance)
            filter: Metadata filter
        """
        import numpy as np
        
        # Fetch more documents than needed
        initial_results = self.similarity_search(
            query_embedding,
            k=fetch_k,
            filter=filter
        )
        
        if not initial_results:
            return []
        
        # Extract ChromaDB IDs from metadata
        ids = [meta.get('chroma_id') for _, _, meta in initial_results]
        
        # Filter out None values
        valid_indices = [i for i, id in enumerate(ids) if id is not None]
        if not valid_indices:
            # If no valid IDs, return initial results without MMR
            return initial_results[:k]
        
        ids = [ids[i] for i in valid_indices]
        initial_results = [initial_results[i] for i in valid_indices]
        
        # Get embeddings for the fetched documents
        results = self.collection.get(
            ids=ids,
            include=["embeddings", "documents", "metadatas"]
        )
        
        doc_embeddings = np.array(results['embeddings'])
        query_emb = np.array(query_embedding)
        
        # MMR algorithm
        selected_indices = []
        remaining_indices = list(range(len(initial_results)))
        
        while len(selected_indices) < k and remaining_indices:
            if not selected_indices:
                # Select the most similar document first
                scores = np.dot(doc_embeddings, query_emb)
                best_idx = remaining_indices[np.argmax(scores[remaining_indices])]
            else:
                # Calculate MMR scores
                mmr_scores = []
                for idx in remaining_indices:
                    # Relevance to query
                    relevance = np.dot(doc_embeddings[idx], query_emb)
                    
                    # Max similarity to already selected documents
                    selected_embs = doc_embeddings[selected_indices]
                    max_sim = np.max(np.dot(selected_embs, doc_embeddings[idx]))
                    
                    # MMR score
                    mmr = lambda_mult * relevance - (1 - lambda_mult) * max_sim
                    mmr_scores.append(mmr)
                
                # Select document with highest MMR score
                best_idx = remaining_indices[np.argmax(mmr_scores)]
            
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
        
        # Return selected documents
        return [initial_results[i] for i in selected_indices]

