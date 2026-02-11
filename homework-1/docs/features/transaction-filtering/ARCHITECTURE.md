# Transaction Filtering Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         HTTP Client                              │
│                    (Browser, curl, etc.)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ GET /api/transactions?filters
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TransactionController                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ @GetMapping("/transactions")                              │  │
│  │ getAllTransactions(                                        │  │
│  │   @RequestParam accountId,                                │  │
│  │   @RequestParam type,                                     │  │
│  │   @RequestParam from,                                     │  │
│  │   @RequestParam to                                        │  │
│  │ )                                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Delegates to
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TransactionService                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ getFilteredTransactions(                                  │  │
│  │   accountId, type, from, to                              │  │
│  │ )                                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Calls repository
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TransactionRepository                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ findByFilters(accountId, type, from, to)                 │  │
│  │                                                           │  │
│  │ 1. Stream all transactions                               │  │
│  │ 2. Filter by accountId (from OR to)                      │  │
│  │ 3. Filter by type                                        │  │
│  │ 4. Filter by from date                                   │  │
│  │ 5. Filter by to date                                     │  │
│  │ 6. Collect and return                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Queries
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              In-Memory Data Store (ConcurrentHashMap)            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ transactions: Map<String, Transaction>                    │  │
│  │ accountBalances: Map<String, BigDecimal>                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow

```
1. Client Request
   │
   ├─ No filters?
   │  └─> getAllTransactions() → Return all
   │
   └─ Has filters?
      └─> getFilteredTransactions()
          │
          ├─ accountId filter
          │  └─> Match fromAccount OR toAccount
          │
          ├─ type filter
          │  └─> Match transaction type
          │
          ├─ from date filter
          │  └─> timestamp >= from
          │
          └─ to date filter
             └─> timestamp <= to
             
      ▼
   Return filtered results
```

## Filter Logic Flow

```
┌─────────────────────────────────────────────┐
│      Start: All Transactions Stream         │
└────────────────┬────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ accountId != null?│
         └───────┬───────────┘
                 │
            Yes  │  No
         ┌───────┴───────┐
         ▼               │
   ┌─────────────┐       │
   │ Filter by   │       │
   │ accountId   │       │
   └─────┬───────┘       │
         │               │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │  type != null? │
         └───────┬───────────┘
                 │
            Yes  │  No
         ┌───────┴───────┐
         ▼               │
   ┌─────────────┐       │
   │ Filter by   │       │
   │    type     │       │
   └─────┬───────┘       │
         │               │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │  from != null? │
         └───────┬───────────┘
                 │
            Yes  │  No
         ┌───────┴───────┐
         ▼               │
   ┌─────────────┐       │
   │ Filter by   │       │
   │  from date  │       │
   └─────┬───────┘       │
         │               │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │   to != null?  │
         └───────┬───────────┘
                 │
            Yes  │  No
         ┌───────┴───────┐
         ▼               │
   ┌─────────────┐       │
   │ Filter by   │       │
   │   to date   │       │
   └─────┬───────┘       │
         │               │
         └───────┬───────┘
                 │
                 ▼
      ┌────────────────────┐
      │ Collect to List    │
      └──────┬─────────────┘
             │
             ▼
      ┌────────────────────┐
      │ Return Results     │
      └────────────────────┘
```

## Data Model

```
Transaction {
    id: String
    fromAccount: String  ◄─┐
    toAccount: String    ◄─┼─ Account ID filter matches either
    amount: BigDecimal   │  │
    currency: String     │  │
    type: TransactionType◄──┼─ Type filter
    timestamp: Instant   ◄──┼─ Date range filters
    status: String       │  │
}                        │  │
                         │  │
Filter Parameters:       │  │
- accountId    ─────────►┘  │
- type         ─────────────►┘
- from (date)  ─────────────►
- to (date)    ─────────────►
```

## Example Queries

### Simple Filter
```
GET /api/transactions?accountId=ACC-001

Flow:
1. Stream all transactions
2. Filter: t.fromAccount == ACC-001 OR t.toAccount == ACC-001
3. Return filtered list
```

### Combined Filters
```
GET /api/transactions?accountId=ACC-001&type=TRANSFER&from=2024-01-01T00:00:00Z

Flow:
1. Stream all transactions
2. Filter: t.fromAccount == ACC-001 OR t.toAccount == ACC-001
3. Filter: t.type == TRANSFER
4. Filter: t.timestamp >= 2024-01-01T00:00:00Z
5. Return filtered list
```

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| No filters | O(n) | Returns all transactions |
| Single filter | O(n) | Single pass through data |
| Multiple filters | O(n) | Single pass, multiple conditions |
| Date comparison | O(1) | Per transaction |
| Type comparison | O(1) | Per transaction |
| Account comparison | O(1) | Per transaction |

Where n = total number of transactions

## Integration Points

```
┌──────────────────┐
│   REST Client    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│   Controller     │────▶│    Service       │
│   Layer          │◀────│    Layer         │
└──────────────────┘     └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Repository     │
                         │   Layer          │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Data Store     │
                         └──────────────────┘
```

## Testing Strategy

```
Unit Tests              Integration Tests          Manual Tests
     │                         │                        │
     │                         │                        │
     ▼                         ▼                        ▼
┌─────────┐            ┌──────────────┐        ┌─────────────┐
│Repository│           │ Full Stack   │        │ examples.sh │
│  Tests   │           │   Tests      │        │examples.http│
└─────────┘            └──────────────┘        └─────────────┘
     │                         │                        │
     │                         │                        │
     └─────────────┬───────────┴────────────────────────┘
                   │
                   ▼
           ┌──────────────┐
           │  All Tests   │
           │    Pass      │
           └──────────────┘
```
