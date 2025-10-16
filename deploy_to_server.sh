#!/bin/bash

# PharmasSky Server Deployment Script
# Server IP: 129.212.140.152
#
# This script will:
# 1. Commit and push changes to GitHub
# 2. Connect to the server via SSH
# 3. Pull latest changes from GitHub
# 4. Rebuild Docker containers
# 5. Run database migrations (including ai_agent)
# 6. Collect static files
# 7. Restart Celery workers
# 8. Test API health
#
# Usage: ./deploy_to_server.sh

echo "🚀 Starting deployment to PharmasSky server..."

# Step 1: Push changes to GitHub
echo ""
echo "📤 Pushing changes to GitHub..."

# Check if there are changes to commit
if [[ -n $(git status -s) ]]; then
    echo "📝 Changes detected, committing..."
    
    # Get commit message from user or use default
    read -p "💬 Enter commit message (or press Enter for default): " COMMIT_MSG
    if [[ -z "$COMMIT_MSG" ]]; then
        COMMIT_MSG="Auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    git add .
    git commit -m "$COMMIT_MSG"
    
    echo "🔼 Pushing to GitHub..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ Changes pushed to GitHub successfully"
    else
        echo "❌ Failed to push to GitHub"
        exit 1
    fi
else
    echo "ℹ️  No changes to commit"
    echo "🔼 Checking if local is behind remote..."
    git fetch origin main
    
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    
    if [ $LOCAL != $REMOTE ]; then
        echo "⚠️  Local is behind remote. Pulling changes first..."
        git pull origin main
    fi
fi

echo ""
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
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to pull from GitHub"
        exit 1
    fi
    
    echo "🐳 Checking Docker services..."
    docker-compose ps
    
    echo "🔄 Restarting Docker services..."
    docker-compose down
    docker-compose up -d --build
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    echo "📊 Checking service status..."
    docker-compose ps
    
    echo ""
    echo "🗄️  Running database migrations..."
    
    # Check for new migrations
    echo "🔍 Checking for new migrations..."
    docker-compose exec -T web python manage.py makemigrations
    
    if [ $? -eq 0 ]; then
        echo "✅ Migration files created/checked"
    else
        echo "⚠️  makemigrations had issues"
    fi
    
    # Run migrations for all apps
    echo "▶️  Applying migrations..."
    docker-compose exec -T web python manage.py migrate
    
    if [ $? -eq 0 ]; then
        echo "✅ All migrations applied successfully"
    else
        echo "❌ Migration failed!"
        exit 1
    fi
    
    # Show migration status
    echo ""
    echo "📋 Migration status:"
    docker-compose exec -T web python manage.py showmigrations ai_agent
    docker-compose exec -T web python manage.py showmigrations offers
    docker-compose exec -T web python manage.py showmigrations invoices
    
    echo ""
    echo "📦 Collecting static files..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    echo ""
    echo "🔄 Restarting Celery workers..."
    docker-compose restart celery
    docker-compose restart celery_beat
    
    if [ $? -eq 0 ]; then
        echo "✅ Celery workers restarted"
    else
        echo "⚠️  Celery restart had issues"
    fi
    
    echo ""
    echo "🩺 Testing API health..."
    curl -f http://localhost:8000/api/health/ || echo "⚠️  API health check failed"
    
    echo ""
    echo "✅ Deployment completed!"
EOF

echo ""
echo "🌐 Testing external access..."
curl -f http://129.212.140.152/ || echo "⚠️  External access test failed"

echo ""
echo "🎉 Deployment script finished!"
echo "🔗 Your app should be available at: http://129.212.140.152/"
