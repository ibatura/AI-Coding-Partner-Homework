## 📋 Overview
Build a customer support ticket management system that imports tickets from multiple file formats, automatically categorizes issues, and assigns priorities.

### Task 1: Multi-Format Ticket Import API

Create a REST API for support tickets with these endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tickets` | Create a new support ticket |
| `POST` | `/tickets/import` | Bulk import from CSV/JSON/XML |
| `GET` | `/tickets` | List all tickets (with filtering) |
| `GET` | `/tickets/:id` | Get specific ticket |
| `PUT` | `/tickets/:id` | Update ticket |
| `DELETE` | `/tickets/:id` | Delete ticket |

**Ticket Model:**
```json
{
  "id": "UUID",
  "customer_id": "string",
  "customer_email": "email",
  "customer_name": "string",
  "subject": "string (1-200 chars)",
  "description": "string (10-2000 chars)",
  "category": "account_access | technical_issue | billing_question | feature_request | bug_report | other",
  "priority": "urgent | high | medium | low",
  "status": "new | in_progress | waiting_customer | resolved | closed",
  "created_at": "datetime",
  "updated_at": "datetime",
  "resolved_at": "datetime (nullable)",
  "assigned_to": "string (nullable)",
  "tags": ["array"],
  "metadata": {
    "source": "web_form | email | api | chat | phone",
    "browser": "string",
    "device_type": "desktop | mobile | tablet"
  }
}
```

**Requirements:**
- Parse CSV, JSON, and XML file formats
- Validate all required fields (email format, string lengths, enums)
- Return bulk import summary: total records, successful, failed with error details
- Handle malformed files gracefully with meaningful error messages
- Use appropriate HTTP status codes (201, 400, 404, etc.)

**Constraints:**
- No test are needed for this task
- No documentation is needed for this task
- Create only short document how-to-run md formated file
- Use as **Tech Stack:** Python Flask
- Use as a home folder: homework-2
- Use best practices for code organization
- Comment your code
- Create a high level plan first and save it in a file with md format
- Create branch and do work there with name: homework-2-submission 


