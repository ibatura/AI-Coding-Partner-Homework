# Transaction Filtering - Quick Reference

## Quick Start

### Get All Transactions
```bash
curl http://localhost:8080/api/transactions
```

### Filter by Account
```bash
curl "http://localhost:8080/api/transactions?accountId=ACC-12345"
```

### Filter by Type
```bash
# Transfers only
curl "http://localhost:8080/api/transactions?type=TRANSFER"

# Deposits only
curl "http://localhost:8080/api/transactions?type=DEPOSIT"

# Withdrawals only
curl "http://localhost:8080/api/transactions?type=WITHDRAWAL"
```

### Filter by Date Range
```bash
# From a specific date
curl "http://localhost:8080/api/transactions?from=2024-01-01T00:00:00Z"

# Up to a specific date
curl "http://localhost:8080/api/transactions?to=2024-01-31T23:59:59Z"

# Between two dates
curl "http://localhost:8080/api/transactions?from=2024-01-01T00:00:00Z&to=2024-01-31T23:59:59Z"
```

### Combine Filters
```bash
# Account + Type
curl "http://localhost:8080/api/transactions?accountId=ACC-12345&type=TRANSFER"

# Account + Date Range
curl "http://localhost:8080/api/transactions?accountId=ACC-12345&from=2024-01-01T00:00:00Z&to=2024-01-31T23:59:59Z"

# Type + Date Range
curl "http://localhost:8080/api/transactions?type=DEPOSIT&from=2024-01-01T00:00:00Z"

# All Filters
curl "http://localhost:8080/api/transactions?accountId=ACC-12345&type=TRANSFER&from=2024-01-01T00:00:00Z&to=2024-01-31T23:59:59Z"
```

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `accountId` | String | Account ID (sender or receiver) | `ACC-12345` |
| `type` | Enum | DEPOSIT, WITHDRAWAL, TRANSFER | `TRANSFER` |
| `from` | ISO DateTime | Start date (inclusive) | `2024-01-01T00:00:00Z` |
| `to` | ISO DateTime | End date (inclusive) | `2024-01-31T23:59:59Z` |

## Common Use Cases

### Monthly Statement
```bash
curl "http://localhost:8080/api/transactions?accountId=ACC-12345&from=2024-01-01T00:00:00Z&to=2024-01-31T23:59:59Z"
```

### Recent Transfers
```bash
curl "http://localhost:8080/api/transactions?type=TRANSFER&from=2024-01-15T00:00:00Z"
```

### Account Activity
```bash
curl "http://localhost:8080/api/transactions?accountId=ACC-12345"
```

### Today's Deposits
```bash
curl "http://localhost:8080/api/transactions?type=DEPOSIT&from=2024-01-15T00:00:00Z&to=2024-01-15T23:59:59Z"
```

## Testing

Run all filtering tests:
```bash
./gradlew test --tests TransactionFilteringIntegrationTest
```

Run specific test:
```bash
./gradlew test --tests TransactionFilteringIntegrationTest.shouldFilterTransactionsByAccountId
```

## Notes

- All filters use AND logic (all conditions must match)
- Account ID matches both sender (`fromAccount`) and receiver (`toAccount`)
- Date range is inclusive on both ends
- Empty result returns `[]` with HTTP 200
- All dates must be in ISO 8601 format
