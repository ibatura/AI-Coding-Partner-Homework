# Transaction Filtering Feature

## Overview

The Transaction Filtering feature allows users to query transactions using various filter criteria through the GET `/api/transactions` endpoint. This feature supports filtering by account ID, transaction type, and date range, with the ability to combine multiple filters.

## Feature Details

### Endpoint

```
GET /api/transactions
```

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `accountId` | String | No | Filter transactions by account ID (matches both fromAccount and toAccount) | `ACC-12345` |
| `type` | TransactionType | No | Filter by transaction type (DEPOSIT, WITHDRAWAL, TRANSFER) | `TRANSFER` |
| `from` | ISO 8601 DateTime | No | Filter transactions from this date/time (inclusive) | `2024-01-01T00:00:00Z` |
| `to` | ISO 8601 DateTime | No | Filter transactions until this date/time (inclusive) | `2024-01-31T23:59:59Z` |

### Transaction Types

- `DEPOSIT` - Money deposited into an account
- `WITHDRAWAL` - Money withdrawn from an account
- `TRANSFER` - Money transferred between accounts

## Usage Examples

### 1. Filter by Account ID

Get all transactions for a specific account (either as sender or receiver):

```bash
curl "http://localhost:8080/api/transactions?accountId=ACC-12345"
```

**Response:**
```json
[
  {
    "id": "txn-001",
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.00,
    "currency": "USD",
    "type": "TRANSFER",
    "timestamp": "2024-01-15T10:30:00Z",
    "status": "completed"
  }
]
```

### 2. Filter by Transaction Type

Get all transfer transactions:

```bash
curl "http://localhost:8080/api/transactions?type=TRANSFER"
```

Get all deposits:

```bash
curl "http://localhost:8080/api/transactions?type=DEPOSIT"
```

### 3. Filter by Date Range

Get transactions within a specific date range:

```bash
curl "http://localhost:8080/api/transactions?from=2024-01-01T00:00:00Z&to=2024-01-31T23:59:59Z"
```

Get transactions from a specific date onwards:

```bash
curl "http://localhost:8080/api/transactions?from=2024-01-15T00:00:00Z"
```

Get transactions up to a specific date:

```bash
curl "http://localhost:8080/api/transactions?to=2024-01-31T23:59:59Z"
```

### 4. Combine Multiple Filters

Get all transfers for a specific account within a date range:

```bash
curl "http://localhost:8080/api/transactions?accountId=ACC-12345&type=TRANSFER&from=2024-01-01T00:00:00Z&to=2024-01-31T23:59:59Z"
```

Get deposits for a specific account:

```bash
curl "http://localhost:8080/api/transactions?accountId=ACC-12345&type=DEPOSIT"
```

### 5. No Filters (Get All Transactions)

```bash
curl "http://localhost:8080/api/transactions"
```

## Implementation Details

### Architecture

The filtering feature is implemented across three layers:

1. **Controller Layer** (`TransactionController.java`)
   - Accepts query parameters
   - Validates parameter types
   - Delegates to service layer

2. **Service Layer** (`TransactionService.java`)
   - Business logic coordination
   - Calls repository with filter parameters

3. **Repository Layer** (`TransactionRepository.java`)
   - Data filtering using Java Streams
   - Supports multiple filter combinations

### Filter Logic

- **Account ID Filter**: Matches transactions where the account ID appears in either `fromAccount` or `toAccount`
- **Type Filter**: Exact match on transaction type enum
- **Date Range Filter**: Inclusive filtering using `Instant` comparison
  - `from` parameter: Includes transactions at or after the specified time
  - `to` parameter: Includes transactions at or before the specified time
- **Multiple Filters**: Applied using AND logic (all conditions must be met)

### Date Format

Dates must be provided in ISO 8601 format with timezone:
- Format: `yyyy-MM-ddTHH:mm:ssZ`
- Example: `2024-01-15T10:30:00Z`
- Timezone: UTC (Z) or with offset (e.g., `+02:00`)

## Error Handling

### Invalid Transaction Type

If an invalid transaction type is provided:

```bash
curl "http://localhost:8080/api/transactions?type=INVALID_TYPE"
```

Returns: HTTP 500 Internal Server Error

### Invalid Date Format

If an invalid date format is provided:

```bash
curl "http://localhost:8080/api/transactions?from=invalid-date"
```

Returns: HTTP 500 Internal Server Error

### No Matches

If no transactions match the filter criteria, an empty array is returned:

```json
[]
```

HTTP Status: 200 OK

## Testing

Comprehensive integration tests are available in:
```
src/test/java/com/banking/transactions/integration/TransactionFilteringIntegrationTest.java
```

### Test Coverage

The test suite covers:
- ✅ Filtering by account ID
- ✅ Filtering by transaction type (DEPOSIT, WITHDRAWAL, TRANSFER)
- ✅ Filtering by date range (from, to, both)
- ✅ Combining multiple filters
- ✅ Account ID matching both fromAccount and toAccount
- ✅ Empty results when no matches found
- ✅ Invalid input handling
- ✅ No filters (returns all transactions)

### Running Tests

```bash
./gradlew test --tests TransactionFilteringIntegrationTest
```

## Performance Considerations

- Current implementation uses in-memory data structure (ConcurrentHashMap)
- Filtering is performed using Java Streams
- For large datasets, consider:
  - Database-level filtering with indexed queries
  - Pagination support
  - Query result caching

## Future Enhancements

Potential improvements for this feature:

1. **Pagination**: Add `page` and `size` parameters for large result sets
2. **Sorting**: Add `sort` parameter (e.g., by timestamp, amount)
3. **Amount Range**: Filter by minimum/maximum transaction amount
4. **Currency Filter**: Filter by transaction currency
5. **Status Filter**: Filter by transaction status (pending, completed, failed)
6. **Partial Account Match**: Support wildcard or partial account ID matching
7. **Multiple Account IDs**: Support filtering by multiple accounts
8. **Response Format**: Add support for CSV or other export formats
9. **Better Error Messages**: Return detailed error messages for invalid parameters
10. **Query Validation**: Add custom validators for date ranges (e.g., from < to)

## API Reference

### Request

```http
GET /api/transactions?accountId={accountId}&type={type}&from={from}&to={to} HTTP/1.1
Host: localhost:8080
Accept: application/json
```

### Response

**Success (200 OK)**

```json
[
  {
    "id": "string",
    "fromAccount": "string",
    "toAccount": "string",
    "amount": 0.00,
    "currency": "string",
    "type": "DEPOSIT|WITHDRAWAL|TRANSFER",
    "timestamp": "2024-01-15T10:30:00Z",
    "status": "string"
  }
]
```

**Error (4xx/5xx)**

```json
{
  "timestamp": "2024-01-15T10:30:00.000+00:00",
  "status": 500,
  "error": "Internal Server Error",
  "path": "/api/transactions"
}
```

## Related Documentation

- [API Documentation](../../README.md)
- [Transaction Validation](../validation/README.md)
- [Getting Started Guide](../../QUICK_START.md)
