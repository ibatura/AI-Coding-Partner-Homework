# Test Suite Plan - Task 3

## Objective

Build a comprehensive test suite for the customer support ticket management system
achieving >85% code coverage across all modules.

## Tech Stack

- **Test Framework:** pytest
- **HTTP Testing:** Flask test client (built-in)
- **Coverage:** pytest-cov (coverage.py wrapper)
- **Fixtures:** pytest fixtures + sample data files (CSV, JSON, XML)

## Test Architecture

```
homework-2/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures (app, client, sample data)
│   ├── test_ticket_model.py     # 9 tests - Data model & validation
│   ├── test_ticket_api.py       # 11 tests - REST API endpoints
│   ├── test_import_csv.py       # 6 tests - CSV parsing
│   ├── test_import_json.py      # 5 tests - JSON parsing
│   ├── test_import_xml.py       # 5 tests - XML parsing
│   ├── test_categorization.py   # 10 tests - Auto-classification engine
│   ├── test_integration.py      # 5 tests - End-to-end workflows
│   ├── test_performance.py      # 5 tests - Benchmark tests
│   └── fixtures/
│       ├── valid_tickets.csv
│       ├── valid_tickets.json
│       ├── valid_tickets.xml
│       ├── invalid_tickets.csv
│       ├── invalid_tickets.json
│       └── invalid_tickets.xml
```

## Test Modules Breakdown

### 1. test_ticket_model (9 tests)

Tests the `Ticket` model and validators.

| # | Test Name | Purpose |
|---|-----------|---------|
| 1 | test_create_ticket_with_valid_data | All required fields produce valid ticket |
| 2 | test_auto_generated_fields | id, created_at, updated_at auto-set |
| 3 | test_default_field_values | status="new", tags=[], metadata={} |
| 4 | test_ticket_to_dict | Serialization returns all fields |
| 5 | test_update_ticket_fields | Partial update modifies only specified fields |
| 6 | test_update_sets_resolved_at | Status change to resolved/closed sets resolved_at |
| 7 | test_apply_classification | Classification result applied correctly |
| 8 | test_validate_required_fields_missing | Missing fields produce errors |
| 9 | test_validate_invalid_enum_values | Invalid category/priority/status rejected |

### 2. test_ticket_api (11 tests)

Tests all REST API endpoints via Flask test client.

| # | Test Name | Purpose |
|---|-----------|---------|
| 1 | test_create_ticket_success | POST /tickets returns 201 |
| 2 | test_create_ticket_validation_error | POST /tickets returns 400 on bad data |
| 3 | test_create_ticket_with_auto_classify | POST /tickets?auto_classify=true |
| 4 | test_list_tickets | GET /tickets returns all tickets |
| 5 | test_list_tickets_with_filters | GET /tickets?status=new&priority=high |
| 6 | test_get_ticket_success | GET /tickets/<id> returns 200 |
| 7 | test_get_ticket_not_found | GET /tickets/<id> returns 404 |
| 8 | test_update_ticket_success | PUT /tickets/<id> returns 200 |
| 9 | test_update_ticket_not_found | PUT /tickets/<id> returns 404 |
| 10 | test_delete_ticket_success | DELETE /tickets/<id> returns 200 |
| 11 | test_delete_ticket_not_found | DELETE /tickets/<id> returns 404 |

### 3. test_import_csv (6 tests)

Tests CSV file parsing and import.

| # | Test Name | Purpose |
|---|-----------|---------|
| 1 | test_import_valid_csv | Valid CSV creates tickets |
| 2 | test_import_csv_with_tags | Semicolon-separated tags parsed correctly |
| 3 | test_import_csv_with_metadata | Dot-notation metadata fields parsed |
| 4 | test_import_csv_partial_failure | Mixed valid/invalid rows |
| 5 | test_import_csv_empty_file | Empty file returns zero total |
| 6 | test_import_csv_via_api | POST /tickets/import with CSV file upload |

### 4. test_import_json (5 tests)

Tests JSON file parsing and import.

| # | Test Name | Purpose |
|---|-----------|---------|
| 1 | test_import_valid_json_array | Direct array format works |
| 2 | test_import_valid_json_object | {"tickets": [...]} format works |
| 3 | test_import_json_partial_failure | Mixed valid/invalid records |
| 4 | test_import_json_invalid_format | Malformed JSON returns error |
| 5 | test_import_json_via_api | POST /tickets/import with JSON file upload |

### 5. test_import_xml (5 tests)

Tests XML file parsing and import.

| # | Test Name | Purpose |
|---|-----------|---------|
| 1 | test_import_valid_xml | Multiple <ticket> elements imported |
| 2 | test_import_single_ticket_xml | Single <ticket> root works |
| 3 | test_import_xml_with_tags | <tags><tag> elements parsed |
| 4 | test_import_xml_partial_failure | Mixed valid/invalid records |
| 5 | test_import_xml_via_api | POST /tickets/import with XML file upload |

### 6. test_categorization (10 tests)

Tests the auto-classification engine.

| # | Test Name | Purpose |
|---|-----------|---------|
| 1 | test_classify_account_access | Login/password keywords -> account_access |
| 2 | test_classify_technical_issue | Error/crash keywords -> technical_issue |
| 3 | test_classify_billing_question | Payment/invoice keywords -> billing_question |
| 4 | test_classify_feature_request | Feature/suggestion keywords -> feature_request |
| 5 | test_classify_bug_report | Defect/reproduce keywords -> bug_report |
| 6 | test_classify_other_fallback | No keywords -> "other" category |
| 7 | test_classify_urgent_priority | Critical/production keywords -> urgent |
| 8 | test_classify_default_medium_priority | No priority keywords -> medium |
| 9 | test_confidence_scoring | Verify confidence value in range [0, 1] |
| 10 | test_classification_reasoning | Reasoning string includes keywords and confidence |

### 7. test_integration (5 tests)

Tests end-to-end workflows across multiple components.

| # | Test Name | Purpose |
|---|-----------|---------|
| 1 | test_create_and_retrieve_ticket | Create ticket -> Get by ID -> verify match |
| 2 | test_import_and_classify | Import CSV -> auto-classify -> verify result |
| 3 | test_update_and_manual_override | Create -> auto-classify -> manual update -> manual_override=True |
| 4 | test_full_ticket_lifecycle | Create -> update status -> resolve -> verify resolved_at |
| 5 | test_filter_after_bulk_import | Import multiple -> filter by category/priority |

### 8. test_performance (5 tests)

Benchmark tests for response time and throughput.

| # | Test Name | Purpose |
|---|-----------|---------|
| 1 | test_create_ticket_response_time | Single create < 50ms |
| 2 | test_bulk_import_100_tickets | 100 tickets imported within time limit |
| 3 | test_classification_throughput | 100 classifications within time limit |
| 4 | test_list_tickets_with_many_records | GET /tickets with 500 tickets < 500ms |
| 5 | test_concurrent_operations | Multiple operations in sequence under time limit |

## Shared Fixtures (conftest.py)

- `app` - Flask application instance (testing config)
- `client` - Flask test client
- `sample_ticket_data` - Valid ticket dict
- `created_ticket` - Pre-created ticket for update/delete tests
- `reset_store` - Auto-reset in-memory store between tests

## Coverage Strategy

Target modules for coverage:
- `app/models/ticket.py` - Model logic
- `app/utils/validators.py` - All validation paths
- `app/services/ticket_service.py` - CRUD operations
- `app/services/import_service.py` - All three parsers
- `app/services/classification_service.py` - Keyword matching
- `app/routes/tickets.py` - All endpoint handlers
- `app/utils/classification_logger.py` - Logging

## Execution

```bash
cd homework-2
pip install pytest pytest-cov
pytest tests/ -v --cov=app --cov-report=term-missing
```
