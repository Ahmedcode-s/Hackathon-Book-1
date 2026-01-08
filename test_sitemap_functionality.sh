#!/bin/bash
# Test script for RAG ingestion pipeline

echo "Testing RAG Ingestion Pipeline with sitemap.xml functionality..."

# Check if we have the required files
if [ ! -f "backend/main.py" ]; then
    echo "Error: backend/main.py not found!"
    exit 1
fi

if [ ! -f "backend/.env.example" ]; then
    echo "Error: backend/.env.example not found!"
    exit 1
fi

echo "Files are in place."

# Check if the main components are present in the code
if grep -q "get_urls_from_sitemap" "backend/main.py"; then
    echo "✓ Sitemap functionality found in main.py"
else
    echo "✗ Sitemap functionality NOT found in main.py"
fi

if grep -q "WEBSITE_URL" "backend/.env.example"; then
    echo "✓ WEBSITE_URL variable found in .env.example"
else
    echo "✗ WEBSITE_URL variable NOT found in .env.example"
fi

if grep -q "config\['website_url'\]" "backend/main.py"; then
    echo "✓ Environment variable loading for website URL found in main.py"
else
    echo "✗ Environment variable loading for website URL NOT found in main.py"
fi

echo "Test completed."