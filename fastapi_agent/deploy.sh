#!/bin/bash

# FastAPI Agent Deployment Script
echo "🚀 Deploying FastAPI Agent..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this script from fastapi_agent directory"
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down fastapi-agent

# Build and start services
echo "🔨 Building and starting FastAPI Agent..."
docker-compose build fastapi-agent
docker-compose up -d fastapi-agent

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 10

# Check if service is running
echo "🔍 Checking service status..."
docker-compose ps fastapi-agent

# Test the service
echo "🧪 Testing service..."
curl -s http://localhost:8001/ > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ FastAPI Agent is running successfully!"
    echo "🌐 API available at: http://localhost:8001"
    echo "📚 API docs at: http://localhost:8001/docs"
else
    echo "❌ FastAPI Agent is not responding"
    echo "📋 Checking logs..."
    docker-compose logs --tail=20 fastapi-agent
fi

# Test chat endpoint
echo "💬 Testing chat endpoint..."
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "مرحبا", "context": {"user_id": 1}}' \
  -s | head -c 100
echo ""

echo "🎉 Deployment completed!"
echo "📋 Available endpoints:"
echo "  POST /agent/chat - Text chat"
echo "  POST /agent/voice - Voice processing"
echo "  POST /agent/process - Smart processing"
echo "  POST /agent/check-availability - Check medicine availability"
echo "  POST /agent/suggest-alternative - Suggest alternatives"
echo "  GET /agent/get-wishlist/{user_id} - Get wishlist"
echo "  GET /agent/get-order-total/{user_id} - Get order total"
