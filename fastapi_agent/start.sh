#!/bin/bash

# FastAPI AI Agent Service Startup Script

echo "🚀 Starting FastAPI AI Agent Service..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp config.env.example .env
    echo "⚠️  Please update .env file with your configuration"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p chroma_db
mkdir -p recordings

# Start the service
echo "🎯 Starting FastAPI service..."
echo "🌐 API will be available at: http://localhost:8001"
echo "📚 API docs at: http://localhost:8001/docs"
echo ""
echo "📋 Available endpoints:"
echo "  POST /agent/chat - Text chat"
echo "  POST /agent/voice - Voice processing"
echo "  POST /agent/process - Smart processing"
echo "  POST /agent/check-availability - Check medicine availability"
echo "  POST /agent/create-order - Create order"
echo "  GET /agent/get-wishlist/{user_id} - Get wishlist"
echo "  GET /agent/get-order-total/{user_id} - Get order total"
echo ""

python main.py
