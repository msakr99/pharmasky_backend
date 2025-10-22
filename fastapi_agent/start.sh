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
python main.py
