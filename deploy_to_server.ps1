# PharmasSky Server Deployment Script - PowerShell Version
# Server IP: 129.212.140.152

Write-Host "🚀 Starting deployment to PharmasSky server..." -ForegroundColor Cyan

# Step 1: Push changes to GitHub
Write-Host ""
Write-Host "📤 Pushing changes to GitHub..." -ForegroundColor Yellow

# Check if there are changes to commit
$gitStatus = git status -s
if ($gitStatus) {
    Write-Host "📝 Changes detected, committing..." -ForegroundColor Green
    
    # Get commit message from user or use default
    $commitMsg = Read-Host "💬 Enter commit message (or press Enter for default)"
    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
        $commitMsg = "Auto-deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }
    
    git add .
    git commit -m $commitMsg
    
    Write-Host "🔼 Pushing to GitHub..." -ForegroundColor Yellow
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Changes pushed to GitHub successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ℹ️  No changes to commit" -ForegroundColor Gray
    Write-Host "🔼 Checking if local is behind remote..." -ForegroundColor Yellow
    git fetch origin main
    
    $local = git rev-parse @
    $remote = git rev-parse "@{u}"
    
    if ($local -ne $remote) {
        Write-Host "⚠️  Local is behind remote. Pulling changes first..." -ForegroundColor Yellow
        git pull origin main
    }
}

Write-Host ""
# Test SSH connection
Write-Host "📡 Testing SSH connection..." -ForegroundColor Yellow

$sshTest = ssh -i ~/.ssh/pharmasky-github-deploy -o ConnectTimeout=10 root@129.212.140.152 'echo "SSH connection successful"' 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH connection established" -ForegroundColor Green
} else {
    Write-Host "❌ SSH connection failed. Please ensure:" -ForegroundColor Red
    Write-Host "   1. SSH key is added to server" -ForegroundColor Yellow
    Write-Host "   2. Server is accessible" -ForegroundColor Yellow
    Write-Host "   3. Key permissions are correct (chmod 600 ~/.ssh/pharmasky-github-deploy)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🔄 Connecting to server and updating..." -ForegroundColor Cyan

# Connect to server and run deployment commands
$deployScript = @'
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
    docker-compose exec -T web python manage.py makemigrations
    docker-compose exec -T web python manage.py migrate
    
    if [ $? -eq 0 ]; then
        echo "✅ Migrations completed successfully"
    else
        echo "⚠️  Migration failed or no migrations needed"
    fi
    
    echo ""
    echo "📦 Collecting static files..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    echo ""
    echo "🩺 Testing API health..."
    curl -f http://localhost:8000/api/health/ || echo "⚠️  API health check failed"
    
    echo ""
    echo "✅ Deployment completed!"
'@

ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152 $deployScript

Write-Host ""
Write-Host "🌐 Testing external access..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://129.212.140.152/" -TimeoutSec 10 -UseBasicParsing
    Write-Host "✅ External access successful" -ForegroundColor Green
} catch {
    Write-Host "⚠️  External access test failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Deployment script finished!" -ForegroundColor Green
Write-Host "🔗 Your app should be available at: http://129.212.140.152/" -ForegroundColor Cyan

