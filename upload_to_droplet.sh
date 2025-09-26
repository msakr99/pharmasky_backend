#!/bin/bash

# Upload script for DigitalOcean droplet deployment
# This script uploads your project files to the droplet

DROPLET_IP="129.212.140.152"
PROJECT_NAME="pharmasky"

echo "🚀 Uploading PharmaScope to DigitalOcean droplet..."

# Create a temporary deployment package
echo "📦 Creating deployment package..."
tar -czf pharmasky-deploy.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='venv' \
    --exclude='staticfiles' \
    --exclude='media' \
    --exclude='*.db' \
    --exclude='node_modules' \
    .

echo "📤 Uploading to droplet..."
scp pharmasky-deploy.tar.gz root@$DROPLET_IP:/tmp/

echo "🔧 Setting up on droplet..."
ssh root@$DROPLET_IP << 'EOF'
    # Create project directory
    mkdir -p /opt/pharmasky
    cd /opt/pharmasky
    
    # Extract files
    tar -xzf /tmp/pharmasky-deploy.tar.gz
    
    # Set permissions
    chown -R root:root /opt/pharmasky
    chmod +x deploy.sh
    chmod +x manage_deployment.sh
    
    echo "✅ Files uploaded successfully to /opt/pharmasky"
    ls -la /opt/pharmasky/
EOF

# Clean up local temp file
rm pharmasky-deploy.tar.gz

echo "🎉 Upload completed! Now SSH into your droplet and run the deployment script."
echo "Commands to run on droplet:"
echo "  ssh root@$DROPLET_IP"
echo "  cd /opt/pharmasky"
echo "  ./deploy.sh"
