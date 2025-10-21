#!/bin/bash
# Quick test script for Max Offers Advanced Search
# Run: bash test_max_offers_search.sh

echo "🔍 Testing Max Offers Advanced Search"
echo "======================================"
echo ""

BASE_URL="http://localhost:8000"
TOKEN="your-auth-token-here"  # استبدله بـ token حقيقي

echo "1️⃣ Testing Hybrid Mode (Default)..."
curl -H "Authorization: Token $TOKEN" \
  "$BASE_URL/offers/max-offers/?q=test&search_mode=hybrid" \
  | jq '.results | length'
echo ""

echo "2️⃣ Testing FTS Mode..."
curl -H "Authorization: Token $TOKEN" \
  "$BASE_URL/offers/max-offers/?q=test&search_mode=fts" \
  | jq '.results | length'
echo ""

echo "3️⃣ Testing Trigram Mode..."
curl -H "Authorization: Token $TOKEN" \
  "$BASE_URL/offers/max-offers/?q=test&search_mode=trigram&min_similarity=0.2" \
  | jq '.results | length'
echo ""

echo "4️⃣ Testing Arabic Search..."
curl -H "Authorization: Token $TOKEN" \
  "$BASE_URL/offers/max-offers/?q=باراسيتامول" \
  | jq '.count'
echo ""

echo "5️⃣ Testing with Typo..."
curl -H "Authorization: Token $TOKEN" \
  "$BASE_URL/offers/max-offers/?q=parasetmol&search_mode=trigram" \
  | jq '.count'
echo ""

echo "✅ Tests completed!"

