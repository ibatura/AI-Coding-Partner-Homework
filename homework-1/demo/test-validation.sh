#!/bin/bash

# Test script for transaction validation
# Demonstrates all validation rules and error responses

BASE_URL="http://localhost:8080"
API_ENDPOINT="$BASE_URL/api/transactions"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Transaction Validation Testing"
echo "=========================================="
echo ""

# Test 1: Valid Transaction
echo -e "${YELLOW}Test 1: Valid Transaction${NC}"
echo "Request: Valid transaction with all correct fields"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.50,
    "currency": "USD",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 2: Negative Amount
echo -e "${YELLOW}Test 2: Negative Amount${NC}"
echo "Request: Amount is negative"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": -100.00,
    "currency": "USD",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 3: Zero Amount
echo -e "${YELLOW}Test 3: Zero Amount${NC}"
echo "Request: Amount is zero"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 0,
    "currency": "USD",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 4: Too Many Decimal Places
echo -e "${YELLOW}Test 4: Too Many Decimal Places${NC}"
echo "Request: Amount has 3 decimal places"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.123,
    "currency": "USD",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 5: Invalid Account Format - Too Short
echo -e "${YELLOW}Test 5: Invalid Account Format (Too Short)${NC}"
echo "Request: Account number too short"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-1234",
    "toAccount": "ACC-67890",
    "amount": 100.00,
    "currency": "USD",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 6: Invalid Account Format - Missing Dash
echo -e "${YELLOW}Test 6: Invalid Account Format (Missing Dash)${NC}"
echo "Request: Account number missing dash"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC12345",
    "toAccount": "ACC-67890",
    "amount": 100.00,
    "currency": "USD",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 7: Invalid Account Format - Special Characters
echo -e "${YELLOW}Test 7: Invalid Account Format (Special Characters)${NC}"
echo "Request: Account number contains special characters"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-123@5",
    "toAccount": "ACC-67890",
    "amount": 100.00,
    "currency": "USD",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 8: Invalid Currency Code
echo -e "${YELLOW}Test 8: Invalid Currency Code${NC}"
echo "Request: Currency code is not valid ISO 4217"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.00,
    "currency": "XYZ",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 9: Multiple Validation Errors
echo -e "${YELLOW}Test 9: Multiple Validation Errors${NC}"
echo "Request: All fields invalid"
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "INVALID",
    "toAccount": "ALSO-INVALID",
    "amount": -100.123,
    "currency": "NOTREAL",
    "type": "TRANSFER"
  }' | jq .
echo ""
echo "---"
echo ""

# Test 10: Valid Currencies
echo -e "${YELLOW}Test 10: Valid Multiple Currencies${NC}"
for currency in USD EUR GBP JPY CHF CAD; do
  echo "Testing currency: $currency"
  STATUS=$(curl -s -w "%{http_code}" -o /dev/null -X POST $API_ENDPOINT \
    -H "Content-Type: application/json" \
    -d "{
      \"fromAccount\": \"ACC-12345\",
      \"toAccount\": \"ACC-67890\",
      \"amount\": 50.00,
      \"currency\": \"$currency\",
      \"type\": \"TRANSFER\"
    }")
  if [ "$STATUS" -eq 201 ]; then
    echo -e "${GREEN}✓ $currency accepted${NC}"
  else
    echo -e "${RED}✗ $currency rejected (HTTP $STATUS)${NC}"
  fi
done
echo ""
echo "---"
echo ""

# Test 11: Valid Account Formats
echo -e "${YELLOW}Test 11: Valid Account Formats${NC}"
for account in "ACC-12345" "ACC-ABCDE" "ACC-A1B2C" "ACC-ab123"; do
  echo "Testing account: $account"
  STATUS=$(curl -s -w "%{http_code}" -o /dev/null -X POST $API_ENDPOINT \
    -H "Content-Type: application/json" \
    -d "{
      \"fromAccount\": \"$account\",
      \"toAccount\": \"ACC-99999\",
      \"amount\": 50.00,
      \"currency\": \"USD\",
      \"type\": \"TRANSFER\"
    }")
  if [ "$STATUS" -eq 201 ]; then
    echo -e "${GREEN}✓ $account accepted${NC}"
  else
    echo -e "${RED}✗ $account rejected (HTTP $STATUS)${NC}"
  fi
done
echo ""
echo "---"
echo ""

echo -e "${GREEN}=========================================="
echo "All validation tests completed!"
echo "==========================================${NC}"
