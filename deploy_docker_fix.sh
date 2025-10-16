#!/bin/bash

# PharmaSky Docker Fix Deployment Script
# This script fixes the Docker build issues and deploys the updated code

set -e  # Exit on error

echo "🚀 Starting PharmaSky Docker Fix Deployment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Stop running containers
echo -e "${YELLOW}Step 1: Stopping running containers...${NC}"
docker-compose down || true

# Step 2: Remove old images
echo -e "${YELLOW}Step 2: Removing old Docker images...${NC}"
docker rmi pharmasky_web pharmasky_celery pharmasky_celery_beat 2>/dev/null || true

# Step 3: Clean Docker system
echo -e "${YELLOW}Step 3: Cleaning Docker system...${NC}"
docker system prune -f

# Step 4: Rebuild images with no cache
echo -e "${YELLOW}Step 4: Rebuilding Docker images (this may take a few minutes)...${NC}"
docker-compose build --no-cache

# Step 5: Start containers
echo -e "${YELLOW}Step 5: Starting containers...${NC}"
docker-compose up -d

# Step 6: Wait for services to start
echo -e "${YELLOW}Step 6: Waiting for services to start...${NC}"
sleep 10

# Step 7: Check if containers are running
echo -e "${YELLOW}Step 7: Checking container status...${NC}"
docker-compose ps

# Step 8: Test OpenAI import
echo -e "${YELLOW}Step 8: Testing OpenAI module...${NC}"
if docker exec pharmasky_web python -c "from openai import OpenAI; print('✅ OpenAI loaded successfully!')" 2>/dev/null; then
    echo -e "${GREEN}✅ OpenAI module is working!${NC}"
else
    echo -e "${RED}❌ OpenAI module failed to load${NC}"
    echo -e "${YELLOW}Installing OpenAI manually...${NC}"
    docker exec pharmasky_web pip install openai>=1.0.0
fi

# Step 9: Show recent logs
echo -e "${YELLOW}Step 9: Showing recent logs...${NC}"
docker-compose logs web --tail=30

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "📊 To monitor logs:"
echo "   docker-compose logs -f web"
echo ""
echo "🔍 To check AI Agent:"
echo "   curl -X POST http://localhost/ai-agent/chat/ -H 'Content-Type: application/json' -H 'Authorization: Token YOUR_TOKEN' -d '{\"message\":\"test\"}'"
echo ""

