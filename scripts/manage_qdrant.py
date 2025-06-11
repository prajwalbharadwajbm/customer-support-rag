#!/usr/bin/env python3
"""
Utility script to manage the Qdrant collection.
Provides commands to create, clear, check status, and get info about the collection.
"""

import sys
import argparse
from utils.clients import get_qdrant_client, get_embeddings_model
from internal.env_utils import SettingEnv
from qdrant_client.http.models import Distance, VectorParams
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QdrantManager:
    def __init__(self):
        """Initialize the Qdrant manager."""
        try:
            self.settings = SettingEnv()
            self.client = get_qdrant_client()
            self.embeddings = get_embeddings_model()
            self.collection_name = self.settings.QDRANT_COLLECTION_NAME
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant manager: {str(e)}")
            raise
    
    def create_collection(self, force=False):
        """Create the Qdrant collection."""
        try:
            if self.client.collection_exists(self.collection_name) and not force:
                print(f"Collection '{self.collection_name}' already exists.")
                print("Use --force to recreate it.")
                return True
            
            if force and self.client.collection_exists(self.collection_name):
                print(f"Deleting existing collection '{self.collection_name}'...")
                self.client.delete_collection(self.collection_name)
            
            print(f"Creating collection '{self.collection_name}'...")
            
            # Get vector size from embeddings
            test_embedding = self.embeddings.embed_query("test")
            vector_size = len(test_embedding)
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                )
            )
            
            print(f"Successfully created collection '{self.collection_name}' with vector size {vector_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False
    
    def clear_collection(self):
        """Clear all data from the collection."""
        try:
            if not self.client.collection_exists(self.collection_name):
                print(f"Collection '{self.collection_name}' does not exist.")
                return False
            
            print(f"Clearing collection '{self.collection_name}'...")
            
            # Get collection info first
            collection_info = self.client.get_collection(self.collection_name)
            points_count = collection_info.points_count
            
            if points_count == 0:
                print("Collection is already empty.")
                return True
            
            # Delete all points by scrolling and deleting in batches
            batch_size = 1000
            deleted_count = 0
            
            while True:
                # Scroll to get point IDs
                records, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=batch_size,
                    with_payload=False,
                    with_vectors=False
                )
                
                if not records:
                    break
                
                # Extract point IDs
                point_ids = [record.id for record in records]
                
                # Delete the batch
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
                
                deleted_count += len(point_ids)
                print(f"Deleted {deleted_count} points...")
                
                if next_offset is None:
                    break
            
            print(f"Successfully cleared {deleted_count} points from collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            return False
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            if not self.client.collection_exists(self.collection_name):
                print(f"Collection '{self.collection_name}' does not exist.")
                return True
            
            print(f"Deleting collection '{self.collection_name}'...")
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete collection '{self.collection_name}'? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Deletion cancelled.")
                return False
            
            self.client.delete_collection(self.collection_name)
            print(f"Successfully deleted collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Manage Qdrant collection")
    parser.add_argument("command", choices=["create", "clear", "delete"], 
                       help="Command to execute")
    parser.add_argument("--force", action="store_true", 
                       help="Force recreation when creating collection")
    
    args = parser.parse_args()
    
    try:
        manager = QdrantManager()
        
        if args.command == "create":
            success = manager.create_collection(force=args.force)
            if not success:
                sys.exit(1)
        elif args.command == "clear":
            success = manager.clear_collection()
            if not success:
                sys.exit(1)
        elif args.command == "delete":
            success = manager.delete_collection()
            if not success:
                sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 