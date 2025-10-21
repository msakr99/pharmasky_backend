#!/bin/bash

# Initialize Ollama with Phi-3 Mini model
# Run this after starting docker-compose

echo "🚀 Initializing Ollama with Phi-3 Mini model..."

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service to be ready..."
sleep 5

# Pull the Phi-3 Mini model
echo "📥 Pulling Phi-3 Mini model (this may take a few minutes)..."
docker-compose exec ollama ollama pull phi3:mini

if [ $? -eq 0 ]; then
    echo "✅ Phi-3 Mini model installed successfully!"
    echo ""
    echo "🧪 Testing the model..."
    docker-compose exec ollama ollama run phi3:mini "مرحبا، كيف حالك؟"
    echo ""
    echo "✨ Ollama is ready to use!"
else
    echo "❌ Failed to install Phi-3 Mini model"
    exit 1
fi

