# Customer Support RAG Application

An AI-powered customer support system that provides intelligent responses based on your document knowledge base using Retrieval-Augmented Generation (RAG).

## Features

- **Smart Document Q&A**: Ask questions and get AI-powered answers from your documents
- **Streaming Responses**: Real-time response generation
- **Follow-up Suggestions**: Automatically suggested related questions
- **Clean Web Interface**: Modern Streamlit-based UI
- **Production Ready**: Dockerized and ready for cloud deployment

## Live Demo

- **Link**: [https://customer-support-rag.streamlit.app]

## Architecture

- **Backend**: FastAPI with RAG pipeline (LangChain + Qdrant)
- **Frontend**: Streamlit web application
- **Vector Database**: Qdrant for document embeddings
- **LLM**: Groq for response generation

## Quick Start (Local Development)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd customer-support-rag
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Create .env file with your API keys
   OPENAI_API_KEY=your_openai_key
   GROQ_API_KEY=your_groq_key
   QDRANT_URL=your_qdrant_url
   ```

4. **Run the backend**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Run the frontend** (in another terminal):
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

## Deployment

### Google Cloud Run (Backend) + Streamlit Cloud (Frontend)

#### Step 1: Deploy Backend to Google Cloud Run

1. **Install Google Cloud CLI**:
   ```bash
   # Install gcloud CLI from https://cloud.google.com/sdk/docs/install
   gcloud auth login
   gcloud config set project <your-project-id>
   ```

2. **Build and Deploy to Cloud Run**:
   ```bash
   # Build the container image
   gcloud builds submit --tag gcr.io/<your-project-id>/customer-support-rag

You can follow gcp deployment guide [here](./docs/GCP_DEPLOYMENT.md)

   # Deploy to Cloud Run
   gcloud run deploy customer-support-rag \
     --image gcr.io/<your-project-id>/customer-support-rag \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8000
   ```

3. **Set Environment Variables**:
   ```bash
   gcloud run services update customer-support-rag \
     --set-env-vars GROQ_API_KEY=your_groq_key,QDRANT_URL=your_qdrant_url \
     --region us-central1
   ```

#### Step 2: Deploy Frontend to Streamlit Cloud

1. **Push code to GitHub**
2. **Go to** [share.streamlit.io](https://share.streamlit.io)
3. **Connect your GitHub repository**
4. **Set main file path**: `frontend/deploy_streamlit.py`
5. **Add secrets**: `BACKEND_URL = "<your-cloud-run-service-url>"`

## Project Structure

```
├── main.py                      # FastAPI application entry point
├── dependencies.py              # Dependency injection
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container definition for backend
├── .dockerignore               # Docker ignore rules
├── .gitignore                  # Git ignore rules
│
├── routes/                     # API route definitions
│   └── chat.py                # Chat streaming endpoint
│
├── models/                     # Pydantic data models
│   ├── chat.py                # Chat message models
│
├── services/                   # Business logic services
├── utils/                      # Utility functions
├── internal/                   # Internal configurations
│
├── frontend/                   # Frontend applications
│   ├── streamlit_app.py       # Local development Streamlit app
│   └── deploy_streamlit.py    # Production Streamlit app
│
├── config/                     # Configuration files
│   └── logging.json           # Logging configuration
│
├── scripts/                    # Data processing scripts
│   ├── document_analyzer.py   # PDF analysis utilities
│   ├── vectorize_documents.py # Document vectorization
│   ├── manage_qdrant.py       # Qdrant database management
│   └── setup_qdrant_collection.py # Qdrant setup
│
└── docs/                       # Documentation
    └── PDF_PROCESSING_README.md # PDF processing guide
```

## Configuration

### Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key
- `GROQ_API_KEY`: Groq API key (if using Groq)
- `QDRANT_URL`: Qdrant database URL
- `QDRANT_API_KEY`: Qdrant API key (if required)

### Backend Configuration

The FastAPI backend runs on port 8000 and includes:
- CORS middleware for frontend communication
- Streaming chat endpoints
- Health checks at `/docs`

### Frontend Configuration

The Streamlit frontend connects to the backend via:
- Environment variable `BACKEND_URL`
- Streamlit secrets for production deployment

## Development

### Adding New Features

1. **Backend**: Add new routes in `routes/` directory
2. **Frontend**: Modify `frontend/streamlit_app.py` for local dev or `frontend/deploy_streamlit.py` for production
3. **Models**: Define new Pydantic models in `models/` directory

### Testing

```bash
# Test backend
curl http://localhost:8000/docs

# Test frontend
streamlit run frontend/streamlit_app.py
```

## Monitoring

- **Google Cloud Run**: Built-in metrics, logging, and monitoring
- **Streamlit Cloud**: Application monitoring
- **Health Checks**: Available at `/docs` endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues:
1. Check the deployment logs in Google Cloud Run/Streamlit Cloud
2. Verify environment variables are set correctly
3. Test the backend API directly at `/docs`
4. Check network connectivity between services

---

Built with ❤️ using FastAPI, Streamlit, and LangChain 