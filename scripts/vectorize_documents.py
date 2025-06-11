#!/usr/bin/env python3
"""
Script to vectorize PDF and DOCX documents and add them to Qdrant database.
This script processes PDF and DOCX files, extracts text, splits into chunks, and stores embeddings.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from utils.clients import get_qdrant_client, get_embeddings_model
from internal.env_utils import SettingEnv
from qdrant_client.http.models import Distance, VectorParams
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentVectorizer:
    def __init__(self):
        """Initialize the document vectorizer with Qdrant and embeddings."""
        try:
            self.settings = SettingEnv()
            self.qdrant_client = get_qdrant_client()
            self.embeddings = get_embeddings_model()
            self.collection_name = self.settings.QDRANT_COLLECTION_NAME
            
            # Text splitter configuration
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,  # Size of each chunk
                chunk_overlap=200,  # Overlap between chunks
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Supported file extensions
            self.supported_extensions = {'.pdf', '.docx'}
            
        except Exception as e:
            logger.error(f"Failed to initialize document vectorizer: {str(e)}")
            raise
    
    def ensure_collection_exists(self) -> bool:
        """Ensure the Qdrant collection exists, create if necessary."""
        try:
            if self.qdrant_client.collection_exists(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists.")
                return True
            
            logger.info(f"Creating collection '{self.collection_name}'...")
            
            # Get vector size from embeddings
            test_embedding = self.embeddings.embed_query("test")
            vector_size = len(test_embedding)
            
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                )
            )
            
            logger.info("Collection created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            return False
    
    def get_file_type(self, file_path: str) -> Optional[str]:
        """Determine the file type from the file extension."""
        file_ext = Path(file_path).suffix.lower()
        if file_ext in self.supported_extensions:
            return file_ext[1:]  # Remove the dot
        return None
    
    def load_pdf_file(self, file_path: str) -> List[Document]:
        """Load a single PDF file and return documents."""
        try:
            logger.info(f"Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from PDF: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Failed to load PDF {file_path}: {str(e)}")
            return []
    
    def load_docx_file(self, file_path: str) -> List[Document]:
        """Load a single DOCX file and return documents."""
        try:
            logger.info(f"Loading DOCX: {file_path}")
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            
            # DOCX loader returns one document, but we'll add some metadata
            for doc in documents:
                doc.metadata['source'] = file_path
                doc.metadata['file_type'] = 'docx'
            
            logger.info(f"Loaded DOCX document: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Failed to load DOCX {file_path}: {str(e)}")
            return []
    
    def load_single_file(self, file_path: str) -> List[Document]:
        """Load a single file (PDF or DOCX) and return documents."""
        file_type = self.get_file_type(file_path)
        
        if file_type == 'pdf':
            return self.load_pdf_file(file_path)
        elif file_type == 'docx':
            return self.load_docx_file(file_path)
        else:
            logger.error(f"Unsupported file type: {file_path}")
            logger.error(f"Supported formats: {', '.join(self.supported_extensions)}")
            return []
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """Load all supported document files from a directory."""
        try:
            logger.info(f"Loading documents from directory: {directory_path}")
            all_documents = []
            
            # Process PDF files
            try:
                logger.info("Loading PDF files...")
                pdf_loader = DirectoryLoader(
                    directory_path,
                    glob="**/*.pdf",
                    loader_cls=PyPDFLoader,
                    show_progress=True
                )
                pdf_documents = pdf_loader.load()
                all_documents.extend(pdf_documents)
                logger.info(f"Loaded {len(pdf_documents)} PDF pages")
            except Exception as e:
                logger.warning(f"Error loading PDFs: {str(e)}")
            
            # Process DOCX files
            try:
                logger.info("Loading DOCX files...")
                docx_loader = DirectoryLoader(
                    directory_path,
                    glob="**/*.docx",
                    loader_cls=Docx2txtLoader,
                    show_progress=True
                )
                docx_documents = docx_loader.load()
                
                # Add file type metadata to DOCX documents
                for doc in docx_documents:
                    doc.metadata['file_type'] = 'docx'
                
                all_documents.extend(docx_documents)
                logger.info(f"Loaded {len(docx_documents)} DOCX documents")
            except Exception as e:
                logger.warning(f"Error loading DOCX files: {str(e)}")
            
            logger.info(f"Total documents loaded from directory: {len(all_documents)}")
            return all_documents
            
        except Exception as e:
            logger.error(f"Failed to load documents from directory {directory_path}: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks."""
        try:
            logger.info("Splitting documents into chunks...")
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            return chunks
        except Exception as e:
            logger.error(f"Failed to split documents: {str(e)}")
            return []
    
    def add_metadata_to_chunks(self, chunks: List[Document], source_info: Optional[str] = None) -> List[Document]:
        """Add additional metadata to document chunks."""
        for i, chunk in enumerate(chunks):
            # Add chunk index
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunk_size"] = len(chunk.page_content)
            
            # Add source info if provided
            if source_info:
                chunk.metadata["source_type"] = source_info
            
            # Add file type if not already present
            if 'file_type' not in chunk.metadata:
                source_path = chunk.metadata.get('source', '')
                file_type = self.get_file_type(source_path)
                if file_type:
                    chunk.metadata['file_type'] = file_type
            
            # Add timestamp
            from datetime import datetime
            chunk.metadata["indexed_at"] = datetime.now().isoformat()
        
        return chunks
    
    def vectorize_and_store(self, chunks: List[Document], batch_size: int = 100) -> bool:
        """Vectorize document chunks and store in Qdrant."""
        try:
            if not chunks:
                logger.warning("No documents to vectorize.")
                return False
            
            logger.info(f"Vectorizing and storing {len(chunks)} chunks...")
            
            # Initialize QdrantVectorStore
            vector_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
                validate_collection_config=False
            )
            
            # Add documents in batches
            total_chunks = len(chunks)
            for i in range(0, total_chunks, batch_size):
                batch = chunks[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_chunks + batch_size - 1) // batch_size
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
                
                # Extract texts and metadatas
                texts = [doc.page_content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                
                # Add to vector store
                vector_store.add_texts(texts, metadatas=metadatas)
                
            logger.info("Successfully stored all chunks in Qdrant!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to vectorize and store documents: {str(e)}")
            return False
    
    def process_single_file(self, file_path: str, source_info: Optional[str] = None) -> bool:
        """Process a single document file end-to-end."""
        try:
            # Load document
            documents = self.load_single_file(file_path)
            if not documents:
                return False
            
            # Split into chunks
            chunks = self.split_documents(documents)
            if not chunks:
                return False
            
            # Add metadata
            chunks = self.add_metadata_to_chunks(chunks, source_info)
            
            # Vectorize and store
            return self.vectorize_and_store(chunks)
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {str(e)}")
            return False
    
    def process_directory(self, directory_path: str, source_info: Optional[str] = None) -> bool:
        """Process all supported document files in a directory end-to-end."""
        try:
            # Load all documents from directory
            documents = self.load_directory(directory_path)
            if not documents:
                return False
            
            # Split into chunks
            chunks = self.split_documents(documents)
            if not chunks:
                return False
            
            # Add metadata
            chunks = self.add_metadata_to_chunks(chunks, source_info)
            
            # Vectorize and store
            return self.vectorize_and_store(chunks)
            
        except Exception as e:
            logger.error(f"Failed to process directory {directory_path}: {str(e)}")
            return False
    
    def get_supported_files_in_directory(self, directory_path: str) -> dict:
        """Get count of supported files in a directory."""
        if not os.path.exists(directory_path):
            return {}
        
        file_counts = {}
        for ext in self.supported_extensions:
            pattern = f"**/*{ext}"
            files = list(Path(directory_path).glob(pattern))
            file_counts[ext[1:]] = len(files)  # Remove dot from extension
        
        return file_counts

def main():
    """Main function to handle command line arguments and process documents."""
    parser = argparse.ArgumentParser(description="Vectorize PDF and DOCX documents and store in Qdrant")
    parser.add_argument("--file", "-f", type=str, help="Path to a single document file (PDF or DOCX)")
    parser.add_argument("--directory", "-d", type=str, help="Path to directory containing document files")
    parser.add_argument("--source-info", "-s", type=str, help="Additional source information to add to metadata")
    parser.add_argument("--list-files", "-l", action="store_true", help="List supported files in directory without processing")
    
    args = parser.parse_args()
    
    if not args.file and not args.directory:
        parser.print_help()
        print("\nError: You must specify either --file or --directory")
        print("Supported formats: PDF (.pdf), Word Documents (.docx)")
        sys.exit(1)
    
    try:
        # Initialize vectorizer
        logger.info("Initializing document vectorizer...")
        vectorizer = DocumentVectorizer()
        
        # If just listing files, do that and exit
        if args.list_files and args.directory:
            if not os.path.exists(args.directory):
                logger.error(f"Directory not found: {args.directory}")
                sys.exit(1)
            
            file_counts = vectorizer.get_supported_files_in_directory(args.directory)
            print(f"\nSupported files in {args.directory}:")
            for file_type, count in file_counts.items():
                print(f"  {file_type.upper()}: {count} files")
            
            total_files = sum(file_counts.values())
            print(f"  Total: {total_files} files")
            sys.exit(0)
        
        # Ensure collection exists
        if not vectorizer.ensure_collection_exists():
            logger.error("Failed to ensure collection exists. Exiting.")
            sys.exit(1)
        
        success = False
        
        if args.file:
            # Process single file
            if not os.path.exists(args.file):
                logger.error(f"File not found: {args.file}")
                sys.exit(1)
            
            file_type = vectorizer.get_file_type(args.file)
            if not file_type:
                logger.error(f"Unsupported file type: {args.file}")
                logger.error(f"Supported formats: {', '.join(vectorizer.supported_extensions)}")
                sys.exit(1)
            
            logger.info(f"Processing {file_type.upper()} file: {args.file}")
            success = vectorizer.process_single_file(args.file, args.source_info)
            
        elif args.directory:
            # Process directory
            if not os.path.exists(args.directory):
                logger.error(f"Directory not found: {args.directory}")
                sys.exit(1)
            
            # Show what files will be processed
            file_counts = vectorizer.get_supported_files_in_directory(args.directory)
            total_files = sum(file_counts.values())
            
            if total_files == 0:
                logger.error(f"No supported files found in {args.directory}")
                logger.error(f"Supported formats: {', '.join(vectorizer.supported_extensions)}")
                sys.exit(1)
            
            print(f"Found files to process:")
            for file_type, count in file_counts.items():
                if count > 0:
                    print(f"  {file_type.upper()}: {count} files")
            print(f"  Total: {total_files} files")
            
            logger.info(f"Processing document directory: {args.directory}")
            success = vectorizer.process_directory(args.directory, args.source_info)
        
        if success:
            print("\nDocument vectorization completed successfully!")
            print("Your documents are now available for querying in the RAG system.")
        else:
            print("\nDocument vectorization failed!")
            print("Please check the logs above for error details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 