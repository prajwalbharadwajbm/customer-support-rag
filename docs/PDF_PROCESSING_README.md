# Document Processing for Customer Support RAG

This guide explains how to process PDF and DOCX documents and add them to your Qdrant vector database for the customer support RAG system.

## Overview

The document processing system consists of three main scripts:

1. `setup_qdrant_collection.py` - Creates the Qdrant collection
2. `vectorize_documents.py` - Processes PDF and DOCX files and stores embeddings
3. `manage_qdrant.py` - Manages the Qdrant collection (status, clear, delete)

## Prerequisites

1. **Environment Variables**: You need to set up your environment variables in a `.env` file:
   ```bash
   # Qdrant Configuration
   QDRANT_API_KEY=your-qdrant-api-key-here
   QDRANT_URL=https://your-cluster.qdrant.tech:6333
   QDRANT_COLLECTION_NAME=customer-support-rag
   
   # Embedding Model Configuration
   EMBEDDING_MODEL_NAME=BAAI/bge-base-en-v1.5
   
   # HuggingFace Configuration
   HF_token=hf_your_huggingface_token_here
   HUGGINGFACEHUB_API_TOKEN=hf_your_huggingface_token_here
   LLM_REPO_ID=mistralai/Mistral-7B-Instruct-v0.3
   ```

2. **Dependencies**: Make sure all required packages are installed:
   ```bash
   pip install -r requirements.txt
   ```

## Step-by-Step Process

### Step 1: Set Up the Qdrant Collection

Before processing PDFs, create the Qdrant collection:

```bash
python setup_qdrant_collection.py
```

This script will:
- Connect to your Qdrant instance
- Create the collection with the correct vector configuration
- Verify the setup

### Step 2: Process Your Document Files

You can process documents in two ways:

#### Option A: Process a Single Document File
```bash
# Process a PDF file
python vectorize_documents.py --file path/to/your/document.pdf

# Process a DOCX file
python vectorize_documents.py --file path/to/your/document.docx
```

#### Option B: Process All Documents in a Directory
```bash
python vectorize_documents.py --directory path/to/your/document/folder
```

This will automatically process both PDF and DOCX files in the directory.

#### Optional: List Files Before Processing
See what files will be processed without actually processing them:
```bash
python vectorize_documents.py --directory path/to/your/folder --list-files
```

#### Optional: Add Source Information
You can add metadata to help categorize your documents:
```bash
python vectorize_documents.py --file manual.pdf --source-info "product-manual"
python vectorize_documents.py --directory support-docs/ --source-info "customer-support"
```

### Step 3: Verify the Data

Check if your data was successfully stored:

```bash
python manage_qdrant.py status
```

This will show:
- Collection existence
- Number of stored vectors
- Storage usage
- Collection health

## Advanced Usage

### Managing Your Collection

#### Check Collection Status
```bash
python manage_qdrant.py status
```

#### Clear All Data (Keep Collection)
```bash
python manage_qdrant.py clear
```

#### Delete Entire Collection
```bash
python manage_qdrant.py delete
```

#### Recreate Collection
```bash
python manage_qdrant.py create --force
```

### Customizing Document Processing

The `vectorize_documents.py` script uses these default settings:

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Batch Size**: 100 documents per batch
- **Supported Formats**: PDF (.pdf), Word Documents (.docx)

You can modify these settings by editing the `DocumentVectorizer` class in `vectorize_documents.py`.

### Metadata Added to Each Document Chunk

Each processed document chunk includes the following metadata:

- `source`: Original file path
- `page`: Page number (for PDFs) or document section (for DOCX)
- `file_type`: File type (pdf or docx)
- `chunk_id`: Sequential chunk identifier
- `chunk_size`: Size of the text chunk
- `source_type`: Custom source information (if provided)
- `indexed_at`: Timestamp when the document was indexed

## Troubleshooting

### Common Issues

1. **Collection Not Found Error**
   ```
   ERROR: Collection 'customer-support-rag' doesn't exist
   ```
   **Solution**: Run `python setup_qdrant_collection.py` first.

2. **Connection Error**
   ```
   ERROR: Failed to connect to Qdrant
   ```
   **Solution**: Check your `QDRANT_URL` and `QDRANT_API_KEY` in the `.env` file.

3. **Document Loading Error**
   ```
   ERROR: Failed to load PDF/DOCX
   ```
   **Solution**: Ensure the document file is not corrupted and is readable. For DOCX files, make sure they're not password-protected.

4. **Unsupported File Format**
   ```
   ERROR: Unsupported file type
   ```
   **Solution**: Currently supported formats are PDF (.pdf) and Word Documents (.docx).

5. **Memory Issues with Large Documents**
   - Process files individually instead of entire directories
   - Reduce batch size in the script
   - Process during off-peak hours

### Checking Logs

All scripts provide detailed logging. Look for:
- INFO messages: Normal operation progress
- WARNING messages: Non-critical issues
- ERROR messages: Problems that need attention

### Validation

After processing, verify your data:

1. **Check collection status**:
   ```bash
   python manage_qdrant.py status
   ```

2. **Test the RAG system**: Start your FastAPI application and try querying the processed documents.

## Performance Tips

1. **Batch Processing**: Process multiple PDFs at once using the directory option
2. **Optimal File Size**: PDFs with 10-50 pages process most efficiently
3. **Network**: Use a stable internet connection for cloud Qdrant instances
4. **Resources**: Ensure sufficient RAM for large document processing

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Set up the collection
python setup_qdrant_collection.py

# 2. Process your customer support manuals (PDF and DOCX)
python vectorize_documents.py --directory ./support-manuals/ --source-info "support-manual"

# 3. Process FAQ documents
python vectorize_documents.py --directory ./faq-docs/ --source-info "faq"

# 4. Check the results
python manage_qdrant.py status

# 5. Start your RAG application
python -m uvicorn main:app --reload
```

Your documents are now ready to be queried through the customer support RAG system!

## File Structure

After processing, your project structure should look like:

```
customer-support-rag/
├── vectorize_documents.py     # Document processing script (PDF & DOCX)
├── vectorize_pdfs.py          # Legacy PDF-only script (still available)
├── setup_qdrant_collection.py # Collection setup
├── manage_qdrant.py           # Collection management
├── your-documents/            # Your document files (PDF & DOCX)
├── .env                       # Environment variables
└── ... (other project files)
``` 