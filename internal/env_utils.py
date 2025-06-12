from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class SettingEnv(BaseSettings):
    """
    Environment settings for the customer support RAG application.
    
    Required variables must be set in environment or .env file.
    Optional variables have sensible defaults.
    """
    
    QDRANT_API_KEY: str  # Example: "your-qdrant-api-key-here"
    QDRANT_URL: str  # Example: "https://your-cluster.qdrant.tech:6333"
    QDRANT_COLLECTION_NAME: str  # Example: "customer_support_docs"
    
    # Required: Embedding Model Configuration
    EMBEDDING_MODEL_NAME: str  # Example: "text-embedding-3-small"
    
    # Required: LLM Configuration (Choose one: Groq or HuggingFace)
    GROQ_API_KEY: Optional[str] = None  # Example: "gsk_your_groq_api_key_here" (Recommended)
    
    # Optional: HuggingFace Configuration (Alternative to Groq)
    HF_token: Optional[str] = None  # Example: "hf_your_huggingface_token_here"
    HUGGINGFACEHUB_API_TOKEN: Optional[str] = None  # Example: "hf_your_huggingface_token_here"
    LLM_REPO_ID: str = "meta-llama/llama-4-scout-17b-16e-instruct"  # Currently supported Groq model (fast & efficient)
    
    # Optional: LangChain Tracing (for debugging and monitoring)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None  # Example: "ls__your_langsmith_api_key"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_PROJECT: str = "customer-support-rag"
    
    # Optional: Model Parameters
    MAX_NEW_TOKENS: int = 4000  # Maximum tokens for response generation
    GPT_TOKENIZER: str = "cl100k_base"  # Tokenizer for GPT models
    TOKEN_LIMIT: int = 8000  # Total token limit for context
    PADDING_TOKEN_SIZE_FOR_MESSAGE_METADATA: int = 100  # Buffer for metadata
    
    # Optional: RAG Parameters
    MAX_DOCUMENTS: int = 5  # Maximum documents to retrieve
    SIMILARITY_THRESHOLD: float = 0.7  # Minimum similarity score for relevance
    HIGH_SEVERITY_THRESHOLD: int = 2  # Threshold for high severity issues
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )
    
