"""Settings management using Pydantic."""

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="RAG System", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    # LLM
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    use_local_llm: bool = Field(default=False, env="USE_LOCAL_LLM")  # Set to False to use fallback mode
    
    # Embedding
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL"
    )
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")

    # Vector Database
    chroma_persist_directory: str = Field(
        default="./chroma_db",
        env="CHROMA_PERSIST_DIRECTORY"
    )
    collection_name: str = Field(default="rag_documents", env="COLLECTION_NAME")

    # Chunking
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")

    # Retrieval
    top_k: int = Field(default=5, env="TOP_K")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")

    # Query Processing
    enable_query_rewriting: bool = Field(default=True, env="ENABLE_QUERY_REWRITING")
    max_query_variants: int = Field(default=3, env="MAX_QUERY_VARIANTS")

    # Reranking
    enable_reranking: bool = Field(default=True, env="ENABLE_RERANKING")
    rerank_top_k: int = Field(default=10, env="RERANK_TOP_K")

    # LangSmith
    langchain_tracing_v2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="rag-system", env="LANGCHAIN_PROJECT")

    # Guardrails
    enable_content_filtering: bool = Field(default=True, env="ENABLE_CONTENT_FILTERING")
    enable_pii_detection: bool = Field(default=True, env="ENABLE_PII_DETECTION")
    max_token_length: int = Field(default=4000, env="MAX_TOKEN_LENGTH")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def load_yaml_config(self, config_path: str = "config/config.yaml") -> dict:
        """Load additional configuration from YAML file."""
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return {}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

