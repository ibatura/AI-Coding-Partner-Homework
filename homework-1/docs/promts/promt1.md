Technology Stack: Java with Spring Boot
Use: homework-1 folder for everything

Task
Create a REST API with the following endpoints:  | Method | Endpoint | Description | |--------|----------|-------------| | `POST` | `/transactions` | Create a new transaction | | `GET` | `/transactions` | List all transactions | | `GET` | `/transactions/:id` | Get a specific transaction by ID | | `GET` | `/accounts/:accountId/balance` | Get account balance |

**Transaction Model:**
```json
{
  "id": "string (auto-generated)",
  "fromAccount": "string",
  "toAccount": "string",
  "amount": "number",
  "currency": "string (ISO 4217: USD, EUR, GBP, etc.)",
  "type": "string (deposit | withdrawal | transfer)",
  "timestamp": "ISO 8601 datetime",
  "status": "string (pending | completed | failed)"
}

**Requirements:** - Use in-memory storage (array or object) — no database required - Validate that amounts are positive numbers - Return appropriate HTTP status codes (200, 201, 400, 404) - Include basic error handling  ---

Notes: Create read me file with architecure there, usefull commands, like to run, test. Keep this file strait, structure and simple