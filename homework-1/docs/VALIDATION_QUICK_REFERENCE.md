# Validation Quick Reference

## Valid Request Examples

### Standard Transfer
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.50,
    "currency": "USD",
    "type": "TRANSFER"
  }'
```

### Different Currencies
```bash
# EUR
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"fromAccount":"ACC-12345","toAccount":"ACC-67890","amount":100.00,"currency":"EUR","type":"TRANSFER"}'

# GBP
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"fromAccount":"ACC-12345","toAccount":"ACC-67890","amount":100.00,"currency":"GBP","type":"TRANSFER"}'

# JPY
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"fromAccount":"ACC-12345","toAccount":"ACC-67890","amount":10000,"currency":"JPY","type":"TRANSFER"}'
```

## Invalid Request Examples

### Negative Amount (❌)
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": -100.00,
    "currency": "USD",
    "type": "TRANSFER"
  }'
```
**Error**: `"Amount must be a positive number"`

### Too Many Decimals (❌)
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.123,
    "currency": "USD",
    "type": "TRANSFER"
  }'
```
**Error**: `"Amount must have maximum 2 decimal places"`

### Invalid Account Format (❌)
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "INVALID123",
    "toAccount": "ACC-67890",
    "amount": 100.00,
    "currency": "USD",
    "type": "TRANSFER"
  }'
```
**Error**: `"Invalid account number format. Must follow format ACC-XXXXX where X is alphanumeric"`

### Invalid Currency (❌)
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.00,
    "currency": "XYZ",
    "type": "TRANSFER"
  }'
```
**Error**: `"Invalid currency code. Must be a valid ISO 4217 currency code (e.g., USD, EUR, GBP, JPY)"`

## Validation Rules Summary

| Field | Rule | Valid Examples | Invalid Examples |
|-------|------|----------------|------------------|
| `amount` | Positive, max 2 decimals | `100.50`, `0.01`, `999999.99` | `-100`, `0`, `100.123` |
| `fromAccount` | Format: `ACC-XXXXX` | `ACC-12345`, `ACC-ABCDE`, `ACC-A1B2C` | `INVALID`, `ACC-123`, `ACC12345` |
| `toAccount` | Format: `ACC-XXXXX` | `ACC-12345`, `ACC-ABCDE`, `ACC-A1B2C` | `INVALID`, `ACC-123`, `ACC12345` |
| `currency` | ISO 4217 codes | `USD`, `EUR`, `GBP`, `JPY` | `XYZ`, `DOLLAR`, `US` |

## Test Commands

```bash
# Run all validation tests
./gradlew test --tests "com.banking.transactions.validation.*"

# Run integration tests
./gradlew test --tests "com.banking.transactions.integration.TransactionValidationIntegrationTest"

# Run comprehensive validation demo
./demo/test-validation.sh

# Start application
java -jar build/libs/transactions-api-1.0.0.jar
```

## Supported Currencies

USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD, CNY, INR, BRL, RUB, KRW, MXN, SGD, HKD, NOK, SEK, DKK, PLN, ZAR, THB, MYR, IDR, and all other ISO 4217 codes.
