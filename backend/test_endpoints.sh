#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base URL - change this if your server runs on a different port
BASE_URL="http://localhost:8000"

echo "Testing API endpoints..."
echo "========================"

# Function to test an endpoint
test_endpoint() {
    local endpoint=$1
    local params=$2
    echo -e "\n${GREEN}Testing ${endpoint}${NC}"
    response=$(curl -s "${BASE_URL}${endpoint}${params}")
    if [ $? -eq 0 ]; then
        echo "Response:"
        echo "$response"
    else
        echo -e "${RED}Failed to connect to ${endpoint}${NC}"
    fi
}

# Test /debug/frontpage
test_endpoint "/debug/frontpage"

# Test /debug/article
echo -e "\n${GREEN}Testing /debug/article${NC}"
response=$(curl -s "${BASE_URL}/debug/article?url=https://krebsonsecurity.com/2025/06/inside-a-dark-adtech-empire-fed-by-fake-captchas/")
echo "Response:"
echo "$response" | jq -r '.html.html' | grep -i "<img"

# Test /debug/comments with a sample HN post ID
test_endpoint "/debug/comments" "?id=1"

# Test /analyze endpoint
echo -e "\n${GREEN}Testing /analyze endpoint${NC}"
echo "This will stream data for 5 seconds..."
curl -s "${BASE_URL}/analyze?limit=1" | head -n 5

echo -e "\n${GREEN}All tests completed!${NC}" 