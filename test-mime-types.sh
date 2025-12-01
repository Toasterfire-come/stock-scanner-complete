#!/bin/bash
# Test MIME types on tradescanpro.com after deployment

echo "========================================"
echo "Testing MIME Types on tradescanpro.com"
echo "========================================"
echo ""

# Test CSS file
echo "1. Testing CSS file MIME type:"
curl -sI "https://tradescanpro.com/static/css/main.d5fc19a7.css" | grep -i "content-type"
echo ""

# Test JS file
echo "2. Testing JS file MIME type:"
curl -sI "https://tradescanpro.com/static/js/main.6b8c4a87.js" | grep -i "content-type"
echo ""

# Test AVIF image
echo "3. Testing AVIF image MIME type:"
curl -sI "https://tradescanpro.com/hero.avif" | grep -i "content-type"
echo ""

# Test WebP image
echo "4. Testing WebP image MIME type:"
curl -sI "https://tradescanpro.com/hero.webp" | grep -i "content-type"
echo ""

# Test main page
echo "5. Testing main page loads:"
STATUS=$(curl -sI "https://tradescanpro.com/" | grep -i "HTTP" | head -1)
echo "$STATUS"
echo ""

# Test .htaccess is working
echo "6. Testing security headers (from .htaccess):"
curl -sI "https://tradescanpro.com/" | grep -i "strict-transport-security"
curl -sI "https://tradescanpro.com/" | grep -i "x-content-type-options"
echo ""

echo "========================================"
echo "Expected Results:"
echo "========================================"
echo "1. CSS: content-type: text/css"
echo "2. JS: content-type: application/javascript"
echo "3. AVIF: content-type: image/avif"
echo "4. WebP: content-type: image/webp"
echo "5. Main page: HTTP/2 200"
echo "6. Security headers present"
echo ""
echo "If you see 'text/html' for CSS/JS, the .htaccess"
echo "file was not deployed or Apache needs restart."
