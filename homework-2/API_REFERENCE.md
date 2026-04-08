# Customer Support Ticket Management System - API Reference

## Overview

Welcome to the Customer Support Ticket Management System API. This reference guide provides comprehensive documentation for API consumers to integrate with our ticketing platform.

**Base URL:** `http://localhost:5000`

**API Version:** 1.0

---

## Table of Contents

1. [Endpoints](#endpoints)
2. [Data Models](#data-models)
3. [Error Handling](#error-handling)
4. [cURL Examples](#curl-examples)

---

## Endpoints

### POST /tickets - Create a Ticket

Create a new customer support ticket.

**Method:** `POST`
**Endpoint:** `/tickets`
**Authentication:** None
**Content-Type:** `application/json`

#### Request Body

```json
{
  "customer_id": "CUST-001",
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "subject": "Cannot login to my account",
  "description": "I've been trying to login for the past hour but keep getting an access denied error.",
  "category": "account_access",
  "priority": "high",
  "status": "new",
  "tags": ["login", "urgent"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome 120",
    "device_type": "desktop"
  }
}
```

#### Response - 201 Created

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "CUST-001",
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "subject": "Cannot login to my account",
  "description": "I've been trying to login for the past hour but keep getting an access denied error.",
  "category": "account_access",
  "priority": "high",
  "status": "new",
  "created_at": "2025-02-08T10:30:00Z",
  "updated_at": "2025-02-08T10:30:00Z",
  "resolved_at": null,
  "assigned_to": null,
  "tags": ["login", "urgent"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome 120",
    "device_type": "desktop"
  },
  "classification_confidence": null,
  "classification_reasoning": null,
  "classification_keywords": [],
  "classified_at": null,
  "manual_override": false
}
```

#### Response - 400 Bad Request (Validation Error)

See [Error Handling - Validation Error](#400-validation-error) section.

---

### GET /tickets - List All Tickets

Retrieve all tickets with optional filtering and pagination.

**Method:** `GET`
**Endpoint:** `/tickets`
**Authentication:** None

#### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by status | `new`, `in_progress`, `resolved` |
| `priority` | string | Filter by priority | `urgent`, `high`, `medium`, `low` |
| `category` | string | Filter by category | `account_access`, `technical_issue` |
| `assigned_to` | string | Filter by assigned agent | `agent-123` |
| `customer_email` | string | Filter by customer email | `john@example.com` |
| `page` | integer | Page number (optional) | `1` |
| `limit` | integer | Results per page (optional) | `20` |

#### Response - 200 OK

```json
{
  "tickets": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "customer_id": "CUST-001",
      "customer_email": "john@example.com",
      "customer_name": "John Doe",
      "subject": "Cannot login to my account",
      "description": "I've been trying to login for the past hour but keep getting an access denied error.",
      "category": "account_access",
      "priority": "high",
      "status": "new",
      "created_at": "2025-02-08T10:30:00Z",
      "updated_at": "2025-02-08T10:30:00Z",
      "resolved_at": null,
      "assigned_to": null,
      "tags": ["login", "urgent"],
      "metadata": {
        "source": "web_form",
        "browser": "Chrome 120",
        "device_type": "desktop"
      },
      "classification_confidence": 0.85,
      "classification_reasoning": "Classified as account_access (high confidence) based on keywords: login, access denied",
      "classification_keywords": ["login", "access denied"],
      "classified_at": "2025-02-08T10:30:05Z",
      "manual_override": false
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "customer_id": "CUST-002",
      "customer_email": "jane@example.com",
      "customer_name": "Jane Smith",
      "subject": "Payment not processed",
      "description": "I tried to pay for my subscription but the payment failed.",
      "category": "billing_question",
      "priority": "high",
      "status": "in_progress",
      "created_at": "2025-02-07T15:20:00Z",
      "updated_at": "2025-02-08T09:00:00Z",
      "resolved_at": null,
      "assigned_to": "agent-456",
      "tags": ["billing", "payment"],
      "metadata": {
        "source": "email",
        "browser": null,
        "device_type": null
      },
      "classification_confidence": 0.92,
      "classification_reasoning": "Classified as billing_question (high confidence) based on keywords: payment, subscription",
      "classification_keywords": ["payment", "subscription"],
      "classified_at": "2025-02-07T15:20:10Z",
      "manual_override": false
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 2,
    "total_pages": 1
  }
}
```

---

### GET /tickets/{id} - Get Ticket by ID

Retrieve a specific ticket by its unique identifier.

**Method:** `GET`
**Endpoint:** `/tickets/{id}`
**Authentication:** None

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string (UUID) | Unique ticket identifier |

#### Response - 200 OK

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "CUST-001",
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "subject": "Cannot login to my account",
  "description": "I've been trying to login for the past hour but keep getting an access denied error.",
  "category": "account_access",
  "priority": "high",
  "status": "new",
  "created_at": "2025-02-08T10:30:00Z",
  "updated_at": "2025-02-08T10:30:00Z",
  "resolved_at": null,
  "assigned_to": null,
  "tags": ["login", "urgent"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome 120",
    "device_type": "desktop"
  },
  "classification_confidence": 0.85,
  "classification_reasoning": "Classified as account_access (high confidence) based on keywords: login, access denied",
  "classification_keywords": ["login", "access denied"],
  "classified_at": "2025-02-08T10:30:05Z",
  "manual_override": false
}
```

#### Response - 404 Not Found

See [Error Handling - Not Found](#404-not-found) section.

---

### PUT /tickets/{id} - Update Ticket

Update an existing ticket. Partial updates are allowed; only send fields you want to change.

**Method:** `PUT`
**Endpoint:** `/tickets/{id}`
**Authentication:** None
**Content-Type:** `application/json`

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string (UUID) | Unique ticket identifier |

#### Request Body (Partial Update Example)

```json
{
  "status": "in_progress",
  "assigned_to": "agent-456",
  "priority": "urgent"
}
```

#### Response - 200 OK

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "CUST-001",
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "subject": "Cannot login to my account",
  "description": "I've been trying to login for the past hour but keep getting an access denied error.",
  "category": "account_access",
  "priority": "urgent",
  "status": "in_progress",
  "created_at": "2025-02-08T10:30:00Z",
  "updated_at": "2025-02-08T11:45:30Z",
  "resolved_at": null,
  "assigned_to": "agent-456",
  "tags": ["login", "urgent"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome 120",
    "device_type": "desktop"
  },
  "classification_confidence": 0.85,
  "classification_reasoning": "Classified as account_access (high confidence) based on keywords: login, access denied",
  "classification_keywords": ["login", "access denied"],
  "classified_at": "2025-02-08T10:30:05Z",
  "manual_override": false
}
```

#### Response - 400 Bad Request (Validation Error)

See [Error Handling - Validation Error](#400-validation-error) section.

#### Response - 404 Not Found

See [Error Handling - Not Found](#404-not-found) section.

---

### DELETE /tickets/{id} - Delete Ticket

Delete a ticket permanently.

**Method:** `DELETE`
**Endpoint:** `/tickets/{id}`
**Authentication:** None

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string (UUID) | Unique ticket identifier |

#### Response - 200 OK

```json
{
  "message": "Ticket deleted successfully",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Response - 404 Not Found

See [Error Handling - Not Found](#404-not-found) section.

---

### POST /tickets/import - Bulk Import Tickets

Import multiple tickets from a file (CSV, JSON, or XML format).

**Method:** `POST`
**Endpoint:** `/tickets/import`
**Authentication:** None
**Content-Type:** `multipart/form-data`

#### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `format` | string | File format (optional if detected by extension) | `csv`, `json`, `xml` |

#### Request Format

The request must include a file upload. The format is detected by:
1. Query parameter `?format=`
2. File extension
3. Content-Type header (text/csv, application/json, text/xml)

**CSV Example:**
```csv
customer_id,customer_email,customer_name,subject,description,category,priority,status,tags
CUST-001,john@example.com,John Doe,Cannot login,I've been trying to login for hours,account_access,high,new,login;urgent
CUST-002,jane@example.com,Jane Smith,Payment issue,Payment not processed,billing_question,high,new,billing;payment
```

**JSON Array Example:**
```json
[
  {
    "customer_id": "CUST-001",
    "customer_email": "john@example.com",
    "customer_name": "John Doe",
    "subject": "Cannot login to my account",
    "description": "I've been trying to login for the past hour but keep getting an access denied error.",
    "category": "account_access",
    "priority": "high",
    "status": "new",
    "tags": ["login", "urgent"]
  },
  {
    "customer_id": "CUST-002",
    "customer_email": "jane@example.com",
    "customer_name": "Jane Smith",
    "subject": "Payment not processed",
    "description": "I tried to pay for my subscription but the payment failed.",
    "category": "billing_question",
    "priority": "high",
    "status": "new",
    "tags": ["billing", "payment"]
  }
]
```

**XML Example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<tickets>
  <ticket>
    <customer_id>CUST-001</customer_id>
    <customer_email>john@example.com</customer_email>
    <customer_name>John Doe</customer_name>
    <subject>Cannot login to my account</subject>
    <description>I've been trying to login for the past hour but keep getting an access denied error.</description>
    <category>account_access</category>
    <priority>high</priority>
    <status>new</status>
    <tags>login,urgent</tags>
  </ticket>
  <ticket>
    <customer_id>CUST-002</customer_id>
    <customer_email>jane@example.com</customer_email>
    <customer_name>Jane Smith</customer_name>
    <subject>Payment not processed</subject>
    <description>I tried to pay for my subscription but the payment failed.</description>
    <category>billing_question</category>
    <priority>high</priority>
    <status>new</status>
    <tags>billing,payment</tags>
  </ticket>
</tickets>
```

#### Response - 200 OK

```json
{
  "total": 3,
  "successful": 2,
  "failed": 1,
  "errors": [
    {
      "row": 2,
      "errors": ["Invalid email format: invalid-email"]
    }
  ]
}
```

#### Response - 400 Bad Request (Unsupported Format)

See [Error Handling - Unsupported Format](#400-unsupported-file-format) section.

---

### POST /tickets/{id}/auto-classify - Auto-Classify Ticket

Automatically classify a ticket based on its subject and description using intelligent keyword analysis.

**Method:** `POST`
**Endpoint:** `/tickets/{id}/auto-classify`
**Authentication:** None

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string (UUID) | Unique ticket identifier |

#### Response - 200 OK

```json
{
  "ticket": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "customer_id": "CUST-001",
    "customer_email": "john@example.com",
    "customer_name": "John Doe",
    "subject": "Cannot login to my account",
    "description": "I've been trying to login for the past hour but keep getting an access denied error.",
    "category": "account_access",
    "priority": "high",
    "status": "new",
    "created_at": "2025-02-08T10:30:00Z",
    "updated_at": "2025-02-08T10:30:00Z",
    "resolved_at": null,
    "assigned_to": null,
    "tags": ["login", "urgent"],
    "metadata": {
      "source": "web_form",
      "browser": "Chrome 120",
      "device_type": "desktop"
    },
    "classification_confidence": 0.85,
    "classification_reasoning": "Classified as account_access (high confidence) based on keywords: login, access denied",
    "classification_keywords": ["login", "access denied"],
    "classified_at": "2025-02-08T10:30:05Z",
    "manual_override": false
  },
  "classification": {
    "category": "account_access",
    "priority": "high",
    "confidence": 0.85,
    "reasoning": "Classified as account_access (high confidence) based on keywords: login, access denied",
    "keywords_found": ["login", "access denied"]
  }
}
```

#### Response - 404 Not Found

See [Error Handling - Not Found](#404-not-found) section.

---

## Data Models

### Ticket Schema

Complete ticket object with all fields, types, and constraints.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `id` | string (UUID) | Auto-generated | UUID format | Unique ticket identifier, automatically generated on creation |
| `customer_id` | string | Yes | Required, non-empty | Customer identifier provided at ticket creation |
| `customer_email` | string | Yes | Valid email format | Customer's email address for communication |
| `customer_name` | string | Yes | Required, non-empty | Customer's full name |
| `subject` | string | Yes | 1-200 characters | Ticket subject line |
| `description` | string | Yes | 10-2000 characters | Detailed description of the issue |
| `category` | enum | Yes | account_access, technical_issue, billing_question, feature_request, bug_report, other | Ticket category classification |
| `priority` | enum | Yes | urgent, high, medium, low | Priority level of the ticket |
| `status` | enum | Yes | new, in_progress, waiting_customer, resolved, closed | Current status of the ticket |
| `created_at` | string (ISO-8601) | Auto-set | RFC 3339 format | Timestamp when ticket was created |
| `updated_at` | string (ISO-8601) | Auto-set | RFC 3339 format | Timestamp of last update |
| `resolved_at` | string (ISO-8601) or null | Optional | RFC 3339 format, nullable | Timestamp when ticket was resolved/closed |
| `assigned_to` | string or null | Optional | Nullable, agent identifier | ID of the support agent assigned to the ticket |
| `tags` | array of strings | Optional | Default: [] | Custom tags for ticket organization |
| `metadata` | object | Optional | See metadata schema below | Additional context and client information |
| `classification_confidence` | float or null | Optional | 0-1 range, nullable | Confidence score of auto-classification (0.0 to 1.0) |
| `classification_reasoning` | string or null | Optional | Nullable | Explanation of classification decision |
| `classification_keywords` | array of strings | Optional | Default: [] | Keywords used for classification |
| `classified_at` | string (ISO-8601) or null | Optional | RFC 3339 format, nullable | Timestamp when ticket was auto-classified |
| `manual_override` | boolean | Optional | Default: false | Whether classification was manually overridden |

### Metadata Schema

The `metadata` object contains client context information:

```json
{
  "source": "web_form",           // Required: web_form, email, api, chat, phone
  "browser": "Chrome 120",         // Optional: browser/client information
  "device_type": "desktop"         // Optional: desktop, mobile, tablet
}
```

### Valid Enumerations

**Category Enum Values:**
- `account_access` - Issues related to account login and access
- `technical_issue` - Technical problems and errors
- `billing_question` - Payment and subscription issues
- `feature_request` - Requests for new features
- `bug_report` - Reports of bugs or defects
- `other` - Miscellaneous issues

**Priority Enum Values:**
- `urgent` - Requires immediate attention
- `high` - High priority, address soon
- `medium` - Normal priority
- `low` - Low priority, address when possible

**Status Enum Values:**
- `new` - Newly created ticket
- `in_progress` - Currently being worked on
- `waiting_customer` - Awaiting customer response
- `resolved` - Issue has been resolved
- `closed` - Ticket is closed

**Source Enum Values:**
- `web_form` - Created via web form
- `email` - Created via email
- `api` - Created via API
- `chat` - Created via chat
- `phone` - Created via phone

**Device Type Values:**
- `desktop` - Desktop computer
- `mobile` - Mobile phone
- `tablet` - Tablet device

---

## Error Handling

All error responses include an error code and descriptive message to help with debugging.

### 400 - Validation Error

Returned when request validation fails.

```json
{
  "error": "Validation failed",
  "details": [
    "customer_email is required",
    "customer_email must be a valid email address",
    "subject must be between 1 and 200 characters",
    "description must be between 10 and 2000 characters",
    "priority must be one of: urgent, high, medium, low"
  ]
}
```

### 400 - Bad Request Body

Returned when the request body is not valid JSON.

```json
{
  "error": "Request body must be valid JSON"
}
```

### 400 - Unsupported File Format

Returned when import file format is not supported.

```json
{
  "error": "Unsupported file format. Use csv, json, or xml"
}
```

### 404 - Not Found

Returned when a ticket cannot be found.

```json
{
  "error": "Ticket not found"
}
```

### 500 - Internal Server Error

Returned for unexpected server errors.

```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred. Please try again later."
}
```

---

## cURL Examples

Complete cURL command examples for all endpoints.

### 1. Create a Ticket

```bash
curl -X POST http://localhost:5000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-001",
    "customer_email": "john@example.com",
    "customer_name": "John Doe",
    "subject": "Cannot login to my account",
    "description": "I'\''ve been trying to login for the past hour but keep getting an access denied error.",
    "category": "account_access",
    "priority": "high",
    "status": "new",
    "tags": ["login", "urgent"],
    "metadata": {
      "source": "web_form",
      "browser": "Chrome 120",
      "device_type": "desktop"
    }
  }'
```

### 2. Get All Tickets

```bash
curl -X GET http://localhost:5000/tickets
```

### 3. Get Tickets with Filters (status=new, priority=high)

```bash
curl -X GET "http://localhost:5000/tickets?status=new&priority=high"
```

Alternative with additional filters:

```bash
curl -X GET "http://localhost:5000/tickets?status=new&priority=high&category=account_access&page=1&limit=20"
```

### 4. Get a Single Ticket by ID

```bash
curl -X GET http://localhost:5000/tickets/550e8400-e29b-41d4-a716-446655440000
```

### 5. Update a Ticket (Change Status and Assign)

```bash
curl -X PUT http://localhost:5000/tickets/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "assigned_to": "agent-456",
    "priority": "urgent"
  }'
```

### 6. Delete a Ticket

```bash
curl -X DELETE http://localhost:5000/tickets/550e8400-e29b-41d4-a716-446655440000
```

### 7. Import Tickets from CSV File

```bash
curl -X POST http://localhost:5000/tickets/import?format=csv \
  -F "file=@tickets.csv"
```

Or without specifying format (auto-detected from file extension):

```bash
curl -X POST http://localhost:5000/tickets/import \
  -F "file=@tickets.csv"
```

**CSV File Content (tickets.csv):**
```
customer_id,customer_email,customer_name,subject,description,category,priority,status,tags
CUST-001,john@example.com,John Doe,Cannot login,I've been trying to login for hours,account_access,high,new,login;urgent
CUST-002,jane@example.com,Jane Smith,Payment issue,Payment not processed,billing_question,high,new,billing;payment
CUST-003,bob@example.com,Bob Johnson,App crashes,Application keeps crashing on startup,technical_issue,urgent,new,crash;bug
```

### 8. Import Tickets from JSON File

```bash
curl -X POST http://localhost:5000/tickets/import?format=json \
  -H "Content-Type: application/json" \
  -F "file=@tickets.json"
```

Or without specifying format:

```bash
curl -X POST http://localhost:5000/tickets/import \
  -F "file=@tickets.json"
```

**JSON File Content (tickets.json):**
```json
[
  {
    "customer_id": "CUST-001",
    "customer_email": "john@example.com",
    "customer_name": "John Doe",
    "subject": "Cannot login to my account",
    "description": "I've been trying to login for the past hour but keep getting an access denied error.",
    "category": "account_access",
    "priority": "high",
    "status": "new",
    "tags": ["login", "urgent"]
  },
  {
    "customer_id": "CUST-002",
    "customer_email": "jane@example.com",
    "customer_name": "Jane Smith",
    "subject": "Payment not processed",
    "description": "I tried to pay for my subscription but the payment failed.",
    "category": "billing_question",
    "priority": "high",
    "status": "new",
    "tags": ["billing", "payment"]
  }
]
```

### 9. Import Tickets from XML File

```bash
curl -X POST http://localhost:5000/tickets/import?format=xml \
  -H "Content-Type: text/xml" \
  -F "file=@tickets.xml"
```

Or with automatic format detection:

```bash
curl -X POST http://localhost:5000/tickets/import \
  -H "Content-Type: text/xml" \
  -F "file=@tickets.xml"
```

**XML File Content (tickets.xml):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<tickets>
  <ticket>
    <customer_id>CUST-001</customer_id>
    <customer_email>john@example.com</customer_email>
    <customer_name>John Doe</customer_name>
    <subject>Cannot login to my account</subject>
    <description>I've been trying to login for the past hour but keep getting an access denied error.</description>
    <category>account_access</category>
    <priority>high</priority>
    <status>new</status>
    <tags>login,urgent</tags>
  </ticket>
  <ticket>
    <customer_id>CUST-002</customer_id>
    <customer_email>jane@example.com</customer_email>
    <customer_name>Jane Smith</customer_name>
    <subject>Payment not processed</subject>
    <description>I tried to pay for my subscription but the payment failed.</description>
    <category>billing_question</category>
    <priority>high</priority>
    <status>new</status>
    <tags>billing,payment</tags>
  </ticket>
</tickets>
```

### 10. Auto-Classify a Ticket

```bash
curl -X POST http://localhost:5000/tickets/550e8400-e29b-41d4-a716-446655440000/auto-classify
```

---

## Best Practices for API Consumers

### Authentication & Security
- Always use HTTPS in production environments
- Validate all input data on the client side before sending
- Handle error responses gracefully with appropriate user feedback

### Rate Limiting
- Implement exponential backoff for retries
- Cache responses when possible to reduce API calls
- Batch operations using the import endpoint for large datasets

### Error Handling
- Always check the HTTP status code
- Parse and display error details from the response
- Log errors for debugging and monitoring

### Data Validation
- Ensure emails are valid before sending
- Verify that subject and description meet length requirements
- Use only valid enum values for category, priority, and status
- Validate tags and metadata structure before submission

### Performance
- Use query parameters to filter results and reduce response size
- Request only necessary fields when possible
- Implement pagination for large datasets using `page` and `limit` parameters

---

## Support & Contact

For API issues, feature requests, or additional support:

- **Email:** support@ticketsystem.com
- **Documentation:** https://docs.ticketsystem.com
- **Status Page:** https://status.ticketsystem.com
