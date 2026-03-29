# Transaction Export Feature

## Overview

The Transaction Export feature allows users to export all transactions in CSV format. This is useful for reporting, data analysis, and integration with external systems like spreadsheets or accounting software.

## Feature Details

### Endpoint

```
GET /api/transactions/export
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `format` | String | No | `csv` | Export format (currently only `csv` is supported) |

### Response

- **Content-Type**: `text/csv`
- **Content-Disposition**: `attachment; filename="transactions.csv"`

### CSV Columns

| Column | Description |
|--------|-------------|
| `id` | Unique transaction identifier |
| `fromAccount` | Source account ID |
| `toAccount` | Destination account ID |
| `amount` | Transaction amount |
| `currency` | Currency code (ISO 4217) |
| `type` | Transaction type (DEPOSIT, WITHDRAWAL, TRANSFER) |
| `timestamp` | ISO 8601 timestamp |
| `status` | Transaction status (pending, completed, failed) |

## Usage Examples

### Export All Transactions as CSV

```bash
curl "http://localhost:8080/api/transactions/export" -o transactions.csv
```

Or with explicit format parameter:

```bash
curl "http://localhost:8080/api/transactions/export?format=csv" -o transactions.csv
```

**Response:**
```csv
id,fromAccount,toAccount,amount,currency,type,timestamp,status
abc-123,ACC-12345,ACC-67890,100.00,USD,TRANSFER,2024-01-15T10:30:00Z,completed
def-456,ACC-00000,ACC-12345,500.00,USD,DEPOSIT,2024-01-14T09:00:00Z,completed
```

### View in Terminal

```bash
curl "http://localhost:8080/api/transactions/export"
```

### Download with Custom Filename

```bash
curl "http://localhost:8080/api/transactions/export" -o my_transactions_$(date +%Y%m%d).csv
```

## Implementation Details

### Architecture

The feature is implemented across two layers:

1. **Controller Layer** (`TransactionController.java`)
   - Accepts the format query parameter
   - Validates the requested format
   - Sets appropriate HTTP headers for file download
   - Returns CSV content with `text/csv` Content-Type

2. **Service Layer** (`TransactionService.java`)
   - Retrieves all transactions from repository
   - Converts transactions to CSV format
   - Handles proper CSV escaping for special characters

### CSV Escaping

The implementation properly handles CSV special characters:
- Fields containing commas are enclosed in double quotes
- Fields containing double quotes have quotes escaped (`"` becomes `""`)
- Fields containing newlines are enclosed in double quotes
- Null values are exported as empty strings

### Error Handling

**Unsupported Format (400 Bad Request)**

```bash
curl "http://localhost:8080/api/transactions/export?format=xml"
```

Response:
```
Unsupported format: xml. Supported formats: csv
```

**No Transactions**

If no transactions exist, the response contains only the header row:
```csv
id,fromAccount,toAccount,amount,currency,type,timestamp,status
```

## API Reference

### Request

```http
GET /api/transactions/export?format=csv HTTP/1.1
Host: localhost:8080
Accept: text/csv
```

### Response

**Success (200 OK)**

Headers:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="transactions.csv"
```

Body:
```csv
id,fromAccount,toAccount,amount,currency,type,timestamp,status
...
```

**Error (400 Bad Request)**

```
Unsupported format: {format}. Supported formats: csv
```

## Future Enhancements

Potential improvements for this feature:

1. **Additional Formats**: Support JSON, XML, or Excel export
2. **Filtering**: Combine with existing filter parameters (accountId, type, date range)
3. **Pagination**: Export in chunks for large datasets
4. **Compression**: Gzip compression for large exports
5. **Async Export**: Background job for very large exports with download link
6. **Custom Columns**: Allow selecting which columns to include
7. **Date Range Filename**: Include date range in exported filename

## Related Documentation

- [API Documentation](../../README.md)
- [Transaction Filtering](../transaction-filtering/README.md)
- [Account Summary](../account-summary/README.md)
