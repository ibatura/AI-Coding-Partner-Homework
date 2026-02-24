# Account Summary Feature

## Overview

The Account Summary feature provides a comprehensive overview of an account's transaction activity through a single endpoint. It returns aggregated statistics including total deposits, total withdrawals, transaction count, and the most recent transaction date.

## Feature Details

### Endpoint

```
GET /api/accounts/{accountId}/summary
```

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `accountId` | String | Yes | The account ID to get summary for | `ACC-12345` |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `accountId` | String | The account ID requested |
| `totalDeposits` | BigDecimal | Sum of all deposits and incoming transfers |
| `totalWithdrawals` | BigDecimal | Sum of all withdrawals and outgoing transfers |
| `transactionCount` | Integer | Total number of transactions involving this account |
| `mostRecentTransactionDate` | ISO 8601 DateTime | Timestamp of the most recent transaction, or null if none |

## Usage Examples

### Get Account Summary

```bash
curl "http://localhost:8080/api/accounts/ACC-12345/summary"
```

**Response:**
```json
{
  "accountId": "ACC-12345",
  "totalDeposits": 5000.00,
  "totalWithdrawals": 1500.00,
  "transactionCount": 8,
  "mostRecentTransactionDate": "2024-01-15T10:30:00Z"
}
```

### Account with No Transactions

```bash
curl "http://localhost:8080/api/accounts/ACC-99999/summary"
```

**Response:**
```json
{
  "accountId": "ACC-99999",
  "totalDeposits": 0,
  "totalWithdrawals": 0,
  "transactionCount": 0,
  "mostRecentTransactionDate": null
}
```

## Implementation Details

### Architecture

The feature is implemented across three layers:

1. **Controller Layer** (`TransactionController.java`)
   - Accepts the account ID path parameter
   - Delegates to service layer
   - Returns HTTP 200 with summary response

2. **Service Layer** (`TransactionService.java`)
   - Retrieves all transactions for the account
   - Calculates aggregated statistics
   - Handles transfer transactions appropriately (incoming as deposits, outgoing as withdrawals)

3. **DTO** (`AccountSummaryResponse.java`)
   - Response data transfer object with summary fields

### Calculation Logic

- **Total Deposits**: Sum of:
  - All `DEPOSIT` transactions where account is `toAccount`
  - All `TRANSFER` transactions where account is `toAccount` (incoming)

- **Total Withdrawals**: Sum of:
  - All `WITHDRAWAL` transactions where account is `fromAccount`
  - All `TRANSFER` transactions where account is `fromAccount` (outgoing)

- **Transaction Count**: Number of all transactions where account appears in either `fromAccount` or `toAccount`

- **Most Recent Transaction Date**: The maximum timestamp among all transactions for the account

## API Reference

### Request

```http
GET /api/accounts/{accountId}/summary HTTP/1.1
Host: localhost:8080
Accept: application/json
```

### Response

**Success (200 OK)**

```json
{
  "accountId": "string",
  "totalDeposits": 0.00,
  "totalWithdrawals": 0.00,
  "transactionCount": 0,
  "mostRecentTransactionDate": "2024-01-15T10:30:00Z"
}
```

## Related Documentation

- [API Documentation](../../README.md)
- [Transaction Filtering](../transaction-filtering/README.md)
