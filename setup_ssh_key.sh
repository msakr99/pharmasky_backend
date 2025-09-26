#!/bin/bash

# Setup SSH key for GitHub Actions deployment
# هذا الملف يقوم بإعداد SSH key على الدروبليت للنشر التلقائي

echo "🔑 إعداد SSH key للنشر التلقائي من GitHub..."

# SSH public key for GitHub Actions
SSH_PUBLIC_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDQH0MsW1lzkRkpbOspKXb1dlpA1hHD8AONnpDGSFtld pharmasky-github-deploy"

# Add the public key to authorized_keys
mkdir -p ~/.ssh
echo "$SSH_PUBLIC_KEY" >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Install git if not already installed
if ! command -v git >/dev/null 2>&1; then
    echo "📦 Installing git..."
    apt update
    apt install -y git
fi

# Create project directory if not exists
if [ ! -d "/opt/pharmasky" ]; then
    echo "📁 Creating project directory..."
    mkdir -p /opt/pharmasky
    
    # Clone the repository
    echo "📥 Cloning repository from GitHub..."
    git clone https://github.com/msakr99/pharmasky_backend.git /opt/pharmasky
    
    # Set proper permissions
    chown -R root:root /opt/pharmasky
    chmod +x /opt/pharmasky/*.sh
else
    echo "📁 Project directory already exists"
fi

echo "✅ SSH key setup completed!"
echo ""
echo "🔍 تم إعداد المفتاح التالي:"
echo "$SSH_PUBLIC_KEY"
echo ""
echo "📝 الخطوات التالية:"
echo "1. أضف المفتاح الخاص إلى GitHub Secrets"
echo "2. تأكد من رفع التغييرات إلى GitHub"
echo "3. اختبر النشر التلقائي"
