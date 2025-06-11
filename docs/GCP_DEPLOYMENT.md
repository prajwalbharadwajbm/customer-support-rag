# Google Cloud Run Deployment Guide

## Overview

Deploy your Customer Support RAG FastAPI application to Google Cloud Run with these advantages:
- **8GB image size limit** (vs Railway's 4GB)
- **Pay-per-request pricing** (cost-effective for ML workloads)
- **Auto-scaling** from 0 to 1000+ instances
- **Built-in load balancing** and **HTTPS**
- **Global deployment** options

## Quick Start

### Prerequisites

1. **Google Cloud Account**: Create one at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud CLI**: Install from [here](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Ensure Docker is running locally

### Step 1: Setup Google Cloud Project

```bash
# Install gcloud CLI (if not already installed)
# macOS
brew install --cask google-cloud-sdk

# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create customer-support-rag-prod --name="Customer Support RAG"

# Set the project
export GOOGLE_CLOUD_PROJECT=customer-support-rag-prod
gcloud config set project $GOOGLE_CLOUD_PROJECT

# List billing accounts
gcloud beta billing accounts list
# Set billing account
gcloud beta billing projects link customer-support-rag-prod --billing-account=019596-000000-000000

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Deploy with One Command

```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Deploy
./deploy-gcp.sh
```

## Manual Deployment Steps

If you prefer manual control:

### 1. Build and Push Image

```bash
# Set variables
PROJECT_ID="your-project-id"
SERVICE_NAME="customer-support-rag"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Build image
docker build -f Dockerfile.cloudrun -t ${IMAGE_NAME}:latest .

# Configure Docker for GCR
gcloud auth configure-docker

# Push image
docker push ${IMAGE_NAME}:latest
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy customer-support-rag \
    --image gcr.io/${PROJECT_ID}/customer-support-rag:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8000 \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300
```

### 3. Set Environment Variables

```bash
gcloud run services update customer-support-rag \
    --region us-central1 \
    --set-env-vars \
    GROQ_API_KEY="your-groq-key",\
    QDRANT_URL="your-qdrant-url",\
    QDRANT_API_KEY="your-qdrant-key",\
    OPENAI_API_KEY="your-openai-key",\
    EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
```

## Using Cloud Build (CI/CD)

For automated deployments, connect your GitHub repository:

### 1. Setup Cloud Build Trigger

```bash
# Connect repository
gcloud builds triggers create github \
    --repo-name="customer-support-rag" \
    --repo-owner="your-github-username" \
    --branch-pattern="main" \
    --build-config="cloudbuild.yaml"
```

### 2. Push to Deploy

Now every push to `main` branch will automatically deploy to Cloud Run!

## 💰 Cost Optimization

Cloud Run pricing is pay-per-request:
- **CPU**: $0.000024 per vCPU-second
- **Memory**: $0.0000025 per GiB-second
- **Requests**: $0.40 per million requests
- **Free tier**: 2 million requests/month

**Example monthly cost** for moderate usage:
- 100K requests/month: ~$2-5
- 1M requests/month: ~$10-20

## 🔒 Security Features

### Authentication (Optional)

To require authentication:

```bash
gcloud run services update customer-support-rag \
    --region us-central1 \
    --no-allow-unauthenticated
```

### Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service customer-support-rag \
    --domain api.yourdomain.com \
    --region us-central1
```

## 📊 Monitoring & Logging

### View Logs

```bash
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=customer-support-rag" --limit 50
```

### Metrics Dashboard

Visit [Cloud Run Console](https://console.cloud.google.com/run) to see:
- Request count
- Response times
- Error rates
- CPU/Memory usage

## Frontend Integration

Update your Streamlit app to use the new Cloud Run URL:

```python
# In your Streamlit app
BACKEND_URL = "https://customer-support-rag-xxxx-uc.a.run.app"
```

## Troubleshooting

### Common Issues

1. **Build fails**: Check `requirements-prod.txt` for conflicts
2. **Memory errors**: Increase memory in deployment config
3. **Timeout errors**: Increase timeout from 300s
4. **Cold starts**: Use min-instances to keep warm

### Debug Commands

```bash
# Check service status
gcloud run services describe customer-support-rag --region us-central1

# View recent logs
gcloud logs tail "resource.type=cloud_run_revision"

# Test locally
docker run -p 8000:8000 -e PORT=8000 gcr.io/$PROJECT_ID/customer-support-rag:latest
```

## Advanced Configuration

### Auto-scaling

```bash
gcloud run services update customer-support-rag \
    --region us-central1 \
    --min-instances 1 \
    --max-instances 100 \
    --concurrency 80
```

### Multiple Regions

Deploy to multiple regions for global coverage:

```bash
# Deploy to Europe
gcloud run deploy customer-support-rag-eu \
    --image gcr.io/$PROJECT_ID/customer-support-rag:latest \
    --region europe-west1 \
    --platform managed \
    --allow-unauthenticated
```

## Support

- **Google Cloud Support**: [cloud.google.com/support](https://cloud.google.com/support)
- **Cloud Run Documentation**: [cloud.google.com/run/docs](https://cloud.google.com/run/docs)
- **Pricing Calculator**: [cloud.google.com/products/calculator](https://cloud.google.com/products/calculator)

---

**Next Steps**: After deployment, update your Streamlit frontend to use the new Cloud Run URL! 