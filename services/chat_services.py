from langchain_qdrant import QdrantVectorStore
from langchain_core.runnables import RunnableParallel,RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from internal.prompt import prompt
from internal.env_utils import SettingEnv
from utils.clients import (
    get_qdrant_client,
    get_embeddings_model,    
    get_model
)
from utils.text_processing import format_docs

settings = SettingEnv()

   
def chat_chain():
    qdrant_client = get_qdrant_client()
    embeddings_model = get_embeddings_model()
    
    # Check if collection exists before creating QdrantVectorStore
    collection_name = settings.QDRANT_COLLECTION_NAME
    if not qdrant_client.collection_exists(collection_name):
        raise RuntimeError(
            f"Qdrant collection '{collection_name}' does not exist. "
            f"Please run 'python setup_qdrant_collection.py' to create it first."
        )
    
    vector_store = QdrantVectorStore(
        qdrant_client, 
        collection_name, 
        embeddings_model,
        validate_collection_config=False  # Disable validation since we already checked
    ).as_retriever()
    llm = get_model()
    
    retrieval_chain = (
        RunnableParallel(
            {
                "context": RunnableLambda(lambda z: z["question"]) | vector_store | format_docs,
                "question": RunnableLambda(lambda z: z["question"])
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return retrieval_chain
  # Return the chain directly, not in a dictionary
