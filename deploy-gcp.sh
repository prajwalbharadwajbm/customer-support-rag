#!/bin/bash

# Google Cloud Run Deployment Script
# Usage: ./deploy-gcp.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
SERVICE_NAME="customer-support-rag"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${YELLOW}🚀 Deploying Customer Support RAG to Google Cloud Run${NC}"

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: GOOGLE_CLOUD_PROJECT environment variable is not set${NC}"
    echo "Please run: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo -e "${YELLOW}Service: ${SERVICE_NAME}${NC}"

# Build the image for x86_64 platform (Cloud Run requirement)
echo -e "${YELLOW}Building Docker image for x86_64 platform...${NC}"
docker build --platform linux/amd64 -f Dockerfile.cloudrun -t ${IMAGE_NAME}:latest .

# Configure Docker for GCR
echo -e "${YELLOW}Configuring Docker for Google Container Registry...${NC}"
gcloud auth configure-docker --quiet

# Push the image
echo -e "${YELLOW}Pushing image to Google Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --port 8000 \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300 \
    --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')

echo -e "${GREEN}Deployment successful!${NC}"
echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}API Docs: ${SERVICE_URL}/docs${NC}"
echo -e "${GREEN}Health Check: ${SERVICE_URL}/health${NC}"

echo -e "${YELLOW}Next steps:${NC}"
echo "1. Set your environment variables in Cloud Run console:"
echo "   - GROQ_API_KEY"
echo "   - QDRANT_URL" 
echo "   - QDRANT_API_KEY"
echo "   - OPENAI_API_KEY"
echo "   - EMBEDDING_MODEL_NAME"
echo ""
echo "2. Update your frontend to use the new URL:"
echo "   ${SERVICE_URL}" 