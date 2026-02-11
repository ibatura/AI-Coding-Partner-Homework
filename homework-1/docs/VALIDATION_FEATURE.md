# Transaction Validation Feature

## Overview
This document describes the validation logic implemented for the Banking Transactions API.

## Validation Rules

### 1. Amount Validation
- **Rule**: Amount must be positive and have maximum 2 decimal places
- **Examples**:
  - ✅ Valid: `100.00`, `0.01`, `999999.99`, `100.5`, `100`
  - ❌ Invalid: `0`, `-100.00`, `100.123`, `0.001`
- **Error Messages**:
  - `"Amount must be a positive number"` - when amount is zero or negative
  - `"Amount must have maximum 2 decimal places"` - when amount has more than 2 decimal places

### 2. Account Number Validation
- **Rule**: Account numbers must follow format `ACC-XXXXX` (where X is alphanumeric)
- **Examples**:
  - ✅ Valid: `ACC-12345`, `ACC-ABCDE`, `ACC-A1B2C`, `ACC-ab123`
  - ❌ Invalid: `ACC-1234` (too short), `ACC-123456` (too long), `ACC12345` (missing dash), `ACC-123@5` (special character)
- **Error Message**: `"Invalid account number format. Must follow format ACC-XXXXX where X is alphanumeric"`

### 3. Currency Validation
- **Rule**: Only accept valid ISO 4217 currency codes
- **Supported Currencies**: USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD, CNY, INR, BRL, RUB, KRW, MXN, SGD, HKD, NOK, SEK, DKK, PLN, ZAR, THB, MYR, IDR, and more
- **Examples**:
  - ✅ Valid: `USD`, `EUR`, `GBP`, `JPY`, `usd` (case insensitive)
  - ❌ Invalid: `XYZ`, `ABC`, `DOLLAR`, `US`, `USDD`
- **Error Message**: `"Invalid currency code. Must be a valid ISO 4217 currency code (e.g., USD, EUR, GBP, JPY)"`

## Error Response Format

### Single Validation Error
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "amount",
      "message": "Amount must be a positive number"
    }
  ]
}
```

### Multiple Validation Errors
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "amount",
      "message": "Amount must be a positive number"
    },
    {
      "field": "currency",
      "message": "Invalid currency code. Must be a valid ISO 4217 currency code (e.g., USD, EUR, GBP, JPY)"
    },
    {
      "field": "fromAccount",
      "message": "Invalid account number format. Must follow format ACC-XXXXX where X is alphanumeric"
    }
  ]
}
```

## Implementation Details

### Custom Validators

1. **@ValidAmount** - Validates transaction amounts
   - Implementation: `AmountValidator.java`
   - Checks: Positive value, max 2 decimal places

2. **@ValidAccountNumber** - Validates account number format
   - Implementation: `AccountNumberValidator.java`
   - Pattern: `^ACC-[A-Za-z0-9]{5}$`

3. **@ValidCurrency** - Validates ISO 4217 currency codes
   - Implementation: `CurrencyValidator.java`
   - Uses predefined list + Java Currency class for validation

### Transaction Model
The `Transaction` model uses Jakarta Bean Validation annotations:
```java
@NotBlank(message = "fromAccount is required")
@ValidAccountNumber
private String fromAccount;

@NotBlank(message = "toAccount is required")
@ValidAccountNumber
private String toAccount;

@NotNull(message = "amount is required")
@ValidAmount
private BigDecimal amount;

@NotBlank(message = "currency is required")
@ValidCurrency
private String currency;
```

### Exception Handling
The `GlobalExceptionHandler` catches `MethodArgumentNotValidException` and transforms it into the standardized error response format.

## Testing

### Unit Tests
- `AmountValidatorTest` - Tests amount validation logic
- `AccountNumberValidatorTest` - Tests account number format validation
- `CurrencyValidatorTest` - Tests currency code validation

### Integration Tests
- `TransactionValidationIntegrationTest` - End-to-end tests for validation with REST API

Run tests:
```bash
# Run all validation tests
./gradlew test --tests "com.banking.transactions.validation.*"

# Run integration tests
./gradlew test --tests "com.banking.transactions.integration.TransactionValidationIntegrationTest"
```

## API Examples

### Valid Request
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

### Invalid Request (Multiple Errors)
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "INVALID",
    "toAccount": "ALSO-INVALID",
    "amount": -100.123,
    "currency": "NOTREAL",
    "type": "TRANSFER"
  }'
```

Response:
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "fromAccount",
      "message": "Invalid account number format. Must follow format ACC-XXXXX where X is alphanumeric"
    },
    {
      "field": "toAccount",
      "message": "Invalid account number format. Must follow format ACC-XXXXX where X is alphanumeric"
    },
    {
      "field": "amount",
      "message": "Amount must be a positive number"
    },
    {
      "field": "currency",
      "message": "Invalid currency code. Must be a valid ISO 4217 currency code (e.g., USD, EUR, GBP, JPY)"
    }
  ]
}
```

## Files Modified/Created

### Created Files
- `src/main/java/com/banking/transactions/validation/ValidAmount.java`
- `src/main/java/com/banking/transactions/validation/AmountValidator.java`
- `src/main/java/com/banking/transactions/validation/ValidAccountNumber.java`
- `src/main/java/com/banking/transactions/validation/AccountNumberValidator.java`
- `src/main/java/com/banking/transactions/validation/ValidCurrency.java`
- `src/main/java/com/banking/transactions/validation/CurrencyValidator.java`
- `src/test/java/com/banking/transactions/validation/AmountValidatorTest.java`
- `src/test/java/com/banking/transactions/validation/AccountNumberValidatorTest.java`
- `src/test/java/com/banking/transactions/validation/CurrencyValidatorTest.java`
- `src/test/java/com/banking/transactions/integration/TransactionValidationIntegrationTest.java`

### Modified Files
- `src/main/java/com/banking/transactions/model/Transaction.java` - Added custom validation annotations
