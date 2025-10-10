#!/bin/bash

# 🚀 Deploy Migration Script
# يرفع الـ migrations الجديدة ويطبقها على السيرفر

# Configuration
DROPLET_IP="129.212.140.152"
DROPLET_USER="root"
PROJECT_PATH="/opt/pharmasky"
SSH_KEY="~/.ssh/pharmasky-github-deploy"

echo "🚀 Starting migration deployment..."
echo ""

# Step 1: Commit and push changes
echo "📝 Step 1: Committing migration files..."
git add profiles/migrations/0002_userprofile_penalty_cashback.py
git add profiles/models.py
git add profiles/admin.py
git add finance/serializers.py
git add finance/views.py
git add finance/PENALTY_CASHBACK_GUIDE.md
git add finance/PENALTY_CASHBACK_README.md
git add finance/COLLECTION_SCHEDULE_API.md
git add finance/COLLECTION_SCHEDULE_QUICK.md
git add finance/INDEX.md
git commit -m "Add penalty & cashback system for collections"

echo "📤 Step 2: Pushing to GitHub..."
git push origin main

echo ""
echo "📡 Step 3: Connecting to server..."

# Step 2: SSH to server and run migration
ssh -i $SSH_KEY $DROPLET_USER@$DROPLET_IP << 'EOF'
    echo "📂 Navigating to project directory..."
    cd /opt/pharmasky || { echo "❌ Project directory not found"; exit 1; }
    
    echo "🔄 Pulling latest changes from GitHub..."
    git stash
    git pull origin main
    
    echo "🐳 Entering Docker container..."
    docker compose exec -T web bash << 'DOCKER_EOF'
        echo "📦 Running migrations..."
        python manage.py migrate profiles
        python manage.py migrate
        
        echo "✅ Migrations completed!"
        exit
DOCKER_EOF
    
    echo "🔄 Restarting Docker services..."
    docker compose restart web
    
    echo "⏳ Waiting for services to start..."
    sleep 5
    
    echo "📊 Checking service status..."
    docker compose ps
    
    echo "✅ Deployment completed!"
EOF

echo ""
echo "════════════════════════════════════════════════════"
echo "✅ Migration deployed successfully!"
echo "════════════════════════════════════════════════════"
echo ""
echo "🔗 API Endpoint:"
echo "   GET http://129.212.140.152/finance/collection-schedule/"
echo ""
echo "📚 Documentation:"
echo "   - finance/PENALTY_CASHBACK_GUIDE.md"
echo "   - finance/COLLECTION_SCHEDULE_API.md"
echo ""

