#!/usr/bin/env python3
"""
Script to create the Qdrant collection for the customer support RAG application.
Run this script before starting the application to ensure the collection exists.
"""

import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from utils.clients import get_qdrant_client, get_embeddings_model
from internal.env_utils import SettingEnv

def create_qdrant_collection():
    """Create the Qdrant collection if it doesn't exist."""
    try:
        print("Initializing Qdrant collection setup...")
        
        # Load settings
        settings = SettingEnv()
        
        # Get Qdrant client
        client = get_qdrant_client()
        
        # Get embeddings model to determine vector size
        embeddings_model = get_embeddings_model()
        
        # Get vector size by creating a test embedding
        print("Determining vector size...")
        test_embedding = embeddings_model.embed_query("test")
        vector_size = len(test_embedding)
        print(f"Vector size: {vector_size}")
        
        collection_name = settings.QDRANT_COLLECTION_NAME
        print(f"Collection name: {collection_name}")
        
        # Check if collection already exists
        if client.collection_exists(collection_name):
            print(f"Collection '{collection_name}' already exists. No action needed.")
            return True
        
        # Create collection with appropriate vector configuration
        print(f"Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            )
        )
        
        print(f"Successfully created collection '{collection_name}'!")
        
        # Verify collection was created
        if client.collection_exists(collection_name):
            print("Collection creation verified.")
            return True
        else:
            print("ERROR: Collection creation failed verification.")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to create collection: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Qdrant Collection Setup ===")
    
    success = create_qdrant_collection()
    
    if success:
        print("\nCollection setup completed successfully!")
        print("You can now start the application.")
        sys.exit(0)
    else:
        print("\nCollection setup failed!")
        print("Please check your Qdrant configuration and try again.")
        sys.exit(1) 