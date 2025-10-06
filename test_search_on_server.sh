#!/bin/bash
# Quick test script to verify search is working on server
# Run this ON THE SERVER after deployment

echo "======================================================================"
echo "اختبار البحث على السيرفر"
echo "======================================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get token from user
echo ""
echo -e "${YELLOW}أدخل الـ Auth Token:${NC}"
read -r TOKEN

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Error: Token is required!${NC}"
    exit 1
fi

# Determine base URL
if docker ps | grep -q pharmasky; then
    BASE_URL="http://localhost:8000"
    echo -e "${BLUE}Detected Docker - using $BASE_URL${NC}"
else
    BASE_URL="http://127.0.0.1:8000"
    echo -e "${BLUE}Using $BASE_URL${NC}"
fi

echo ""
echo "======================================================================"
echo -e "${YELLOW}Test 1: Get all max offers (no search)${NC}"
echo "======================================================================"

RESPONSE1=$(curl -s -H "Authorization: Token $TOKEN" "$BASE_URL/offers/max-offers/")
COUNT1=$(echo $RESPONSE1 | jq -r '.count' 2>/dev/null || echo "ERROR")

if [ "$COUNT1" = "ERROR" ]; then
    echo -e "${RED}✗ Failed to get response or parse JSON${NC}"
    echo "Response: $RESPONSE1"
else
    echo -e "${GREEN}✓ Total max offers: $COUNT1${NC}"
fi

echo ""
echo "======================================================================"
echo -e "${YELLOW}Test 2: Search with Arabic letter 'ا'${NC}"
echo "======================================================================"

RESPONSE2=$(curl -s -H "Authorization: Token $TOKEN" "$BASE_URL/offers/max-offers/?search=ا")
COUNT2=$(echo $RESPONSE2 | jq -r '.count' 2>/dev/null || echo "ERROR")

if [ "$COUNT2" = "ERROR" ]; then
    echo -e "${RED}✗ Failed to get response or parse JSON${NC}"
else
    echo -e "${GREEN}✓ Offers with 'ا': $COUNT2${NC}"
fi

echo ""
echo "======================================================================"
echo -e "${YELLOW}Test 3: Search with specific term 'استبرين'${NC}"
echo "======================================================================"

RESPONSE3=$(curl -s -H "Authorization: Token $TOKEN" "$BASE_URL/offers/max-offers/?search=استبرين")
COUNT3=$(echo $RESPONSE3 | jq -r '.count' 2>/dev/null || echo "ERROR")

if [ "$COUNT3" = "ERROR" ]; then
    echo -e "${RED}✗ Failed to get response or parse JSON${NC}"
else
    echo -e "${GREEN}✓ Offers with 'استبرين': $COUNT3${NC}"
fi

echo ""
echo "======================================================================"
echo -e "${YELLOW}Test 4: Check application logs${NC}"
echo "======================================================================"

echo "Looking for MaxOfferListAPIView logs..."
if docker ps | grep -q pharmasky; then
    echo "Last 10 MaxOfferListAPIView log entries:"
    docker-compose logs --tail=50 pharmasky_web | grep MaxOfferListAPIView | tail -10
else
    if [ -f /var/log/pharmasky/application.log ]; then
        tail -50 /var/log/pharmasky/application.log | grep MaxOfferListAPIView | tail -10
    else
        echo -e "${YELLOW}Log file not found. Check journalctl:${NC}"
        journalctl -u pharmasky --since "5 minutes ago" | grep MaxOfferListAPIView | tail -10
    fi
fi

echo ""
echo "======================================================================"
echo -e "${YELLOW}RESULTS ANALYSIS${NC}"
echo "======================================================================"

if [ "$COUNT1" != "ERROR" ] && [ "$COUNT2" != "ERROR" ] && [ "$COUNT3" != "ERROR" ]; then
    echo ""
    echo "Test 1 (no search):     $COUNT1 offers"
    echo "Test 2 (search 'ا'):     $COUNT2 offers"
    echo "Test 3 (search 'استبرين'): $COUNT3 offers"
    echo ""
    
    if [ "$COUNT2" -lt "$COUNT1" ] || [ "$COUNT3" -lt "$COUNT1" ]; then
        echo -e "${GREEN}✓✓✓ SUCCESS! Search is working correctly!${NC}"
        echo -e "${GREEN}    Search results are less than total offers${NC}"
    else
        echo -e "${RED}✗✗✗ PROBLEM! Search may not be working!${NC}"
        echo -e "${RED}    All searches return the same count as total offers${NC}"
        echo ""
        echo "Possible issues:"
        echo "  1. Code not updated on server (run 'git pull')"
        echo "  2. Server not restarted (restart Docker/systemd)"
        echo "  3. Wrong code version deployed"
    fi
else
    echo -e "${RED}Could not complete tests due to errors${NC}"
fi

echo ""
echo "======================================================================"

