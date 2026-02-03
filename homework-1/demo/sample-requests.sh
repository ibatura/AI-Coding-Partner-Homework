#!/bin/bash

BASE_URL="http://localhost:8080/api"

echo "🧪 Testing Banking Transactions API"
echo "===================================="
echo ""
echo "Make sure the application is running on port 8080!"
echo ""

# Check if API is running
echo "Checking if API is available..."
if ! curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/transactions" | grep -q "200"; then
    echo "❌ API is not running or not responding at $BASE_URL"
    echo "Please start the application first using: ./demo/run.sh"
    exit 1
fi

echo "✅ API is running!"
echo ""

# 1. Create a deposit transaction
echo "1️⃣  Creating deposit transaction (1000.00 to ACC-12345)..."
RESPONSE=$(curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-00000",
    "toAccount": "ACC-12345",
    "amount": 1000.00,
    "currency": "USD",
    "type": "deposit"
  }')
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

sleep 1

# 2. Create a transfer transaction
echo "2️⃣  Creating transfer transaction (250.75 from ACC-12345 to ACC-67890)..."
RESPONSE=$(curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 250.75,
    "currency": "USD",
    "type": "transfer"
  }')
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

sleep 1

# 3. Create a withdrawal transaction
echo "3️⃣  Creating withdrawal transaction (50.00 from ACC-67890)..."
RESPONSE=$(curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-67890",
    "toAccount": "ACC-00000",
    "amount": 50.00,
    "currency": "USD",
    "type": "withdrawal"
  }')
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

sleep 1

# 4. Get all transactions
echo "4️⃣  Getting all transactions..."
RESPONSE=$(curl -s -X GET "$BASE_URL/transactions")
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

sleep 1

# 5. Get account balance
echo "5️⃣  Getting balance for ACC-12345..."
RESPONSE=$(curl -s -X GET "$BASE_URL/accounts/ACC-12345/balance")
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo "Expected: 749.25 (1000.00 - 250.75)"
echo ""

sleep 1

echo "6️⃣  Getting balance for ACC-67890..."
RESPONSE=$(curl -s -X GET "$BASE_URL/accounts/ACC-67890/balance")
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo "Expected: 200.75 (250.75 - 50.00)"
echo ""

sleep 1

# 7. Test validation error - negative amount
echo "7️⃣  Testing validation (negative amount - should fail)..."
RESPONSE=$(curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": -100.00,
    "currency": "USD",
    "type": "transfer"
  }')
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

sleep 1

# 8. Test validation error - missing fields
echo "8️⃣  Testing validation (missing toAccount field - should fail)..."
RESPONSE=$(curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "amount": 100.00,
    "currency": "USD",
    "type": "transfer"
  }')
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

echo "=================================="
echo "✅ All tests completed!"
echo ""
echo "Summary:"
echo "  - Created 3 transactions (deposit, transfer, withdrawal)"
echo "  - Retrieved all transactions"
echo "  - Checked account balances"
echo "  - Validated error handling"
