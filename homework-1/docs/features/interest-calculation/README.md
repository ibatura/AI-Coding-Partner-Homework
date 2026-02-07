# Simple Interest Calculation Feature

## Overview

The Simple Interest Calculation feature allows users to calculate the interest that would accrue on an account's current balance over a specified period at a given rate. This is useful for financial planning, projections, and understanding potential earnings.

## Feature Details

### Endpoint

```
GET /api/accounts/{accountId}/interest
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accountId` | String | Yes | The account ID to calculate interest for |

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `rate` | BigDecimal | Yes | Annual interest rate as decimal (e.g., 0.05 for 5%) | `0.05` |
| `days` | Integer | Yes | Number of days to calculate interest for | `30` |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `accountId` | String | The account ID |
| `principal` | BigDecimal | Current account balance (principal amount) |
| `rate` | BigDecimal | The interest rate used |
| `days` | Integer | Number of days for calculation |
| `interest` | BigDecimal | Calculated interest amount |
| `finalBalance` | BigDecimal | Principal + Interest |
| `currency` | String | Currency code |

### Formula

Simple Interest is calculated using:

```
Interest = Principal × Rate × (Days / 365)
```

## Usage Examples

### Calculate 30-Day Interest at 5%

```bash
curl "http://localhost:8080/api/accounts/ACC-12345/interest?rate=0.05&days=30"
```

**Response:**
```json
{
  "accountId": "ACC-12345",
  "principal": 10000.00,
  "rate": 0.05,
  "days": 30,
  "interest": 41.10,
  "finalBalance": 10041.10,
  "currency": "USD"
}
```

### Calculate 1-Year Interest at 3.5%

```bash
curl "http://localhost:8080/api/accounts/ACC-12345/interest?rate=0.035&days=365"
```

**Response:**
```json
{
  "accountId": "ACC-12345",
  "principal": 10000.00,
  "rate": 0.035,
  "days": 365,
  "interest": 350.00,
  "finalBalance": 10350.00,
  "currency": "USD"
}
```

### Calculate 90-Day Interest at 2%

```bash
curl "http://localhost:8080/api/accounts/ACC-12345/interest?rate=0.02&days=90"
```

**Response:**
```json
{
  "accountId": "ACC-12345",
  "principal": 5000.00,
  "rate": 0.02,
  "days": 90,
  "interest": 24.66,
  "finalBalance": 5024.66,
  "currency": "USD"
}
```

## Implementation Details

### Architecture

The feature is implemented across three layers:

1. **Controller Layer** (`TransactionController.java`)
   - Accepts path parameter (accountId) and query parameters (rate, days)
   - Delegates to service layer
   - Returns HTTP 200 with interest calculation response

2. **Service Layer** (`TransactionService.java`)
   - Retrieves current account balance from repository
   - Applies simple interest formula
   - Rounds to 2 decimal places using HALF_UP rounding

3. **DTO** (`InterestCalculationResponse.java`)
   - Response data transfer object with all calculation details

### Calculation Details

- Uses 365-day year for interest calculation
- Results rounded to 2 decimal places
- HALF_UP rounding mode (standard financial rounding)
- Account balance of zero results in zero interest

### Error Handling

**Missing Parameters (400 Bad Request)**

If rate or days parameters are missing, Spring returns a validation error.

**Account with No Balance**

Accounts with zero balance return zero interest:
```json
{
  "accountId": "ACC-99999",
  "principal": 0,
  "rate": 0.05,
  "days": 30,
  "interest": 0.00,
  "finalBalance": 0.00,
  "currency": "USD"
}
```

## API Reference

### Request

```http
GET /api/accounts/{accountId}/interest?rate={rate}&days={days} HTTP/1.1
Host: localhost:8080
Accept: application/json
```

### Response

**Success (200 OK)**

```json
{
  "accountId": "string",
  "principal": 0.00,
  "rate": 0.00,
  "days": 0,
  "interest": 0.00,
  "finalBalance": 0.00,
  "currency": "string"
}
```

## Future Enhancements

Potential improvements for this feature:

1. **Compound Interest**: Add option for compound interest calculation
2. **Custom Compounding Period**: Daily, monthly, quarterly compounding
3. **Interest Rate Validation**: Validate rate is within reasonable bounds
4. **Historical Calculation**: Calculate interest based on historical balances
5. **Multiple Currencies**: Support different currency interest rates
6. **Day Count Conventions**: Support 360-day year (actual/360) for some calculations

## Related Documentation

- [API Documentation](../../README.md)
- [Account Balance](../account-balance/README.md)
- [Account Summary](../account-summary/README.md)
