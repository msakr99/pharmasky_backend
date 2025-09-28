#!/bin/bash

# PharmasSky Server Deployment Script
# Server IP: 129.212.140.152

echo "🚀 Starting deployment to PharmasSky server..."

# Test SSH connection
echo "📡 Testing SSH connection..."
if ssh -i ~/.ssh/pharmasky-github-deploy -o ConnectTimeout=10 root@129.212.140.152 'echo "SSH connection successful"'; then
    echo "✅ SSH connection established"
else
    echo "❌ SSH connection failed. Please ensure:"
    echo "   1. SSH key is added to server"
    echo "   2. Server is accessible"
    echo "   3. Key permissions are correct (chmod 600 ~/.ssh/pharmasky-github-deploy)"
    exit 1
fi

echo ""
echo "🔄 Connecting to server and updating..."

# Connect to server and run deployment commands
ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152 << 'EOF'
    echo "📂 Navigating to project directory..."
    cd /opt/pharmasky || { echo "❌ Project directory not found"; exit 1; }
    
    echo "🔄 Pulling latest changes from GitHub..."
    git pull origin main
    
    echo "🐳 Checking Docker services..."
    docker-compose ps
    
    echo "🔄 Restarting Docker services..."
    docker-compose down
    docker-compose up -d --build
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "📊 Checking service status..."
    docker-compose ps
    
    echo "🩺 Testing API health..."
    curl -f http://localhost:8000/api/health/ || echo "⚠️  API health check failed"
    
    echo "✅ Deployment completed!"
EOF

echo ""
echo "🌐 Testing external access..."
curl -f http://129.212.140.152/ || echo "⚠️  External access test failed"

echo ""
echo "🎉 Deployment script finished!"
echo "🔗 Your app should be available at: http://129.212.140.152/"
