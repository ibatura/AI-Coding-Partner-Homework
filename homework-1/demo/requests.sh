#!/bin/bash

BASE_URL="http://localhost:8080/api"

echo "🧪 Testing Banking Transactions API"
echo "===================================="
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
    "type": "DEPOSIT"
  }')
echo -e "\n"

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
    "type": "WITHDRAWAL"
  }')
echo -e "\n"

sleep 1

# 3. Get all transactions
echo "3️⃣  Getting all transactions..."
curl -X GET "$BASE_URL/transactions"
echo -e "\n"

sleep 1

# 4. Get account balance
echo "4️⃣  Getting balance for ACC-12345..."
curl -X GET "$BASE_URL/accounts/ACC-12345/balance"
echo -e "\n"

sleep 1

echo "5️⃣  Getting balance for ACC-67890..."
curl -X GET "$BASE_URL/accounts/ACC-67890/balance"
echo -e "\n"

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
    "type": "TRANSFER"
  }')
echo -e "\n"

echo ""
echo "✅ All tests completed!"
