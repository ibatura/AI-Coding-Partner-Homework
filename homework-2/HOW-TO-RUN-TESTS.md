# How to Run Tests

## Prerequisites

- Python 3.11+
- pip

## Setup

```bash
cd homework-2
pip install -r requirements.txt
```

## Run All Tests

```bash
pytest tests/ -v
```

## Run with Coverage Report

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Run a Specific Test File

```bash
pytest tests/test_ticket_api.py -v
```

## Run a Specific Test

```bash
pytest tests/test_ticket_model.py::TestTicketModel::test_create_ticket_with_valid_data -v
```

## Generate HTML Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```
