# 🚀 Deploy Migration to Server - PowerShell Script
# Deploy penalty & cashback system migrations

Write-Host "🚀 Starting migration deployment to server..." -ForegroundColor Green
Write-Host ""

$DROPLET_IP = "129.212.140.152"
$DROPLET_USER = "root"
$PROJECT_PATH = "/opt/pharmasky"
$SSH_KEY = "$HOME\.ssh\pharmasky-github-deploy"

Write-Host "📡 Connecting to server: $DROPLET_USER@$DROPLET_IP" -ForegroundColor Cyan
Write-Host ""

# SSH commands to run on server
$commands = @"
cd $PROJECT_PATH
echo '🔄 Pulling latest changes from GitHub...'
git stash
git pull origin main

echo '🐳 Running migrations in Docker container...'
docker compose exec -T web python manage.py migrate profiles
docker compose exec -T web python manage.py migrate

echo '🔄 Restarting web service...'
docker compose restart web

echo '⏳ Waiting for service to start...'
sleep 5

echo '📊 Checking service status...'
docker compose ps

echo '✅ Migration deployment completed!'
"@

# Execute commands on server
ssh -i $SSH_KEY "$DROPLET_USER@$DROPLET_IP" $commands

Write-Host ""
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Migration deployed successfully!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Test the API:" -ForegroundColor Yellow
Write-Host "   GET http://129.212.140.152/finance/collection-schedule/" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "   - finance/PENALTY_CASHBACK_GUIDE.md" -ForegroundColor White
Write-Host "   - finance/COLLECTION_SCHEDULE_API.md" -ForegroundColor White
Write-Host ""

