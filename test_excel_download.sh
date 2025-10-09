#!/bin/bash
# Test Excel download endpoint

echo "=========================================="
echo "اختبار تحميل Excel لـ Max Offers"
echo "=========================================="

# Get token from user
echo ""
echo "أدخل الـ Auth Token:"
read -r TOKEN

if [ -z "$TOKEN" ]; then
    echo "Error: Token is required!"
    exit 1
fi

BASE_URL="http://129.212.140.152"

echo ""
echo "=========================================="
echo "Test 1: Download all max offers (Excel)"
echo "=========================================="

curl -H "Authorization: Token $TOKEN" \
     -H "Accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
     "$BASE_URL/offers/max-offers/excel/" \
     -o "max_offers_all.xlsx" \
     -w "\nHTTP Status: %{http_code}\nSize: %{size_download} bytes\n"

if [ -f "max_offers_all.xlsx" ]; then
    echo "✓ File downloaded: max_offers_all.xlsx"
    ls -lh max_offers_all.xlsx
else
    echo "✗ Download failed!"
fi

echo ""
echo "=========================================="
echo "Test 2: Download with search (Excel)"
echo "=========================================="

curl -H "Authorization: Token $TOKEN" \
     -H "Accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
     "$BASE_URL/offers/max-offers/excel/?search=ا" \
     -o "max_offers_search.xlsx" \
     -w "\nHTTP Status: %{http_code}\nSize: %{size_download} bytes\n"

if [ -f "max_offers_search.xlsx" ]; then
    echo "✓ File downloaded: max_offers_search.xlsx"
    ls -lh max_offers_search.xlsx
else
    echo "✗ Download failed!"
fi

echo ""
echo "=========================================="
echo "Done! Check the downloaded files."
echo "=========================================="


