#!/bin/bash
# Script to deploy security fixes on pharmasky-server
# Run this script on the server: bash deploy_fixes.sh

set -e  # Exit on any error

echo "🚀 Starting deployment of security fixes..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Navigating to project directory...${NC}"
cd /opt/pharmasky || { echo -e "${RED}Failed to navigate to /opt/pharmasky${NC}"; exit 1; }
echo -e "${GREEN}✓ In project directory${NC}"
echo ""

echo -e "${YELLOW}Step 2: Fixing migrations permissions...${NC}"
sudo chown -R 1000:1000 ./market/migrations ./core/migrations
sudo chmod -R 775 ./*/migrations
echo -e "${GREEN}✓ Permissions fixed${NC}"
echo ""

echo -e "${YELLOW}Step 3: Pulling latest code from Git...${NC}"
git pull origin main
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

echo -e "${YELLOW}Step 4: Stopping containers...${NC}"
docker-compose down
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

echo -e "${YELLOW}Step 5: Rebuilding and starting containers...${NC}"
docker-compose up -d --build
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

echo -e "${YELLOW}Step 6: Waiting for services to be ready...${NC}"
sleep 10
echo -e "${GREEN}✓ Services should be ready${NC}"
echo ""

echo -e "${YELLOW}Step 7: Running migrations...${NC}"
docker exec -i pharmasky_web python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations completed${NC}"
echo ""

echo -e "${YELLOW}Step 8: Collecting static files...${NC}"
docker exec -i pharmasky_web python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

echo -e "${YELLOW}Step 9: Checking container status...${NC}"
docker-compose ps
echo ""

echo -e "${YELLOW}Step 10: Checking recent logs...${NC}"
docker logs pharmasky_web --tail 30
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}Testing endpoints:${NC}"
echo "• Main API: curl http://localhost:8000/"
echo "• Robots.txt: curl http://localhost:8000/robots.txt"
echo ""

echo -e "${YELLOW}Monitor logs with:${NC}"
echo "docker logs pharmasky_web --tail 50 -f"

