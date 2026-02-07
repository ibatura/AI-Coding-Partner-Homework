#!/bin/bash

# Transaction Filtering Examples
# Make sure the application is running on http://localhost:8080

BASE_URL="http://localhost:8080/api"

echo "==================================="
echo "Transaction Filtering Examples"
echo "==================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create some test transactions first
echo -e "${BLUE}Creating test transactions...${NC}"
curl -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-001",
    "toAccount": "ACC-002",
    "amount": 100.00,
    "currency": "USD",
    "type": "TRANSFER"
  }' -s > /dev/null

curl -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-001",
    "toAccount": "ACC-003",
    "amount": 50.00,
    "currency": "USD",
    "type": "TRANSFER"
  }' -s > /dev/null

curl -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-002",
    "toAccount": "ACC-004",
    "amount": 200.00,
    "currency": "USD",
    "type": "DEPOSIT"
  }' -s > /dev/null

curl -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-003",
    "toAccount": "ACC-005",
    "amount": 75.00,
    "currency": "USD",
    "type": "WITHDRAWAL"
  }' -s > /dev/null

echo -e "${GREEN}Test transactions created!${NC}"
echo ""

# Example 1: Get all transactions
echo -e "${BLUE}1. Get all transactions:${NC}"
echo "curl \"$BASE_URL/transactions\""
curl -s "$BASE_URL/transactions" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

# Example 2: Filter by account ID
echo -e "${BLUE}2. Filter by account ID (ACC-001):${NC}"
echo "curl \"$BASE_URL/transactions?accountId=ACC-001\""
curl -s "$BASE_URL/transactions?accountId=ACC-001" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

# Example 3: Filter by transaction type
echo -e "${BLUE}3. Filter by type (TRANSFER):${NC}"
echo "curl \"$BASE_URL/transactions?type=TRANSFER\""
curl -s "$BASE_URL/transactions?type=TRANSFER" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

# Example 4: Filter by type (DEPOSIT)
echo -e "${BLUE}4. Filter by type (DEPOSIT):${NC}"
echo "curl \"$BASE_URL/transactions?type=DEPOSIT\""
curl -s "$BASE_URL/transactions?type=DEPOSIT" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

# Example 5: Filter by date (from last hour)
echo -e "${BLUE}5. Filter by date (from last hour):${NC}"
FROM_DATE=$(date -u -v-1H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d '1 hour ago' +"%Y-%m-%dT%H:%M:%SZ")
echo "curl \"$BASE_URL/transactions?from=$FROM_DATE\""
curl -s "$BASE_URL/transactions?from=$FROM_DATE" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

# Example 6: Combine filters (account + type)
echo -e "${BLUE}6. Combine filters - Account + Type:${NC}"
echo "curl \"$BASE_URL/transactions?accountId=ACC-001&type=TRANSFER\""
curl -s "$BASE_URL/transactions?accountId=ACC-001&type=TRANSFER" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

# Example 7: Combine filters (account + date range)
echo -e "${BLUE}7. Combine filters - Account + Date Range:${NC}"
FROM_DATE=$(date -u -v-1H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d '1 hour ago' +"%Y-%m-%dT%H:%M:%SZ")
TO_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "curl \"$BASE_URL/transactions?accountId=ACC-001&from=$FROM_DATE&to=$TO_DATE\""
curl -s "$BASE_URL/transactions?accountId=ACC-001&from=$FROM_DATE&to=$TO_DATE" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

# Example 8: All filters combined
echo -e "${BLUE}8. All filters combined:${NC}"
echo "curl \"$BASE_URL/transactions?accountId=ACC-001&type=TRANSFER&from=$FROM_DATE&to=$TO_DATE\""
curl -s "$BASE_URL/transactions?accountId=ACC-001&type=TRANSFER&from=$FROM_DATE&to=$TO_DATE" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

# Example 9: No matches
echo -e "${BLUE}9. No matches (non-existent account):${NC}"
echo "curl \"$BASE_URL/transactions?accountId=ACC-999\""
curl -s "$BASE_URL/transactions?accountId=ACC-999" | python3 -m json.tool
echo ""
echo "-----------------------------------"
echo ""

echo -e "${GREEN}All examples completed!${NC}"
