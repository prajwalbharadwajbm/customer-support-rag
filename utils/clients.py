from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from internal.env_utils import SettingEnv
import logging

logger = logging.getLogger(__name__)
settings = SettingEnv()

from utils.error_handler import ApplicationError

def get_qdrant_client() -> QdrantClient:
    """Initialize Qdrant client
    
    Returns:
        QdrantClient: Initialized Qdrant client
    
    Raises:
        ApplicationError: If client initialization fails
    """
    try:
        return QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing Qdrant client: {str(e)}")
        raise ApplicationError(f"Failed to initialize Qdrant client: {str(e)}") from e

def get_embeddings_model() -> HuggingFaceEmbeddings:
    """Initialize HuggingFace embeddings model
    
    Returns:
        HuggingFaceEmbeddings: Initialized embeddings model
    
    Raises:
        ApplicationError: If model initialization fails
    """
    try:
        return HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={"trust_remote_code": True, "device": "cpu"}
        )
    except Exception as e:
        logger.error(f"Error initializing embeddings model: {str(e)}")
        raise ApplicationError(f"Failed to initialize embeddings model: {str(e)}") from e

def get_model() -> ChatGroq:
    """Initialize Mistral model via Groq
    
    Returns:
        ChatGroq: Initialized Mistral model
    
    Raises:
        ApplicationError: If model initialization fails
    """
    try:
        return ChatGroq(
            model=settings.LLM_REPO_ID,  # Fast, reliable Mixtral model
            temperature=0.1,
            max_tokens=settings.MAX_NEW_TOKENS,
            groq_api_key=settings.GROQ_API_KEY
        )
    except Exception as e:
        logger.error(f"Error initializing Mistral model: {str(e)}")
        raise ApplicationError(f"Failed to initialize Mistral model: {str(e)}") from e