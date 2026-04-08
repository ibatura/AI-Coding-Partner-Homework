# Banking Parser Helpers

Crack open the `banking_parser` package to normalize transaction feeds and run fraud detection heuristics across CSV, JSON, or XML exports.

## Architecture Overview
```mermaid
flowchart TD
    subgraph Parser Layer
        Formats((formats.py))
        Model((model.py))
    end
    subgraph Ingestion
        Load(\"load_transactions_from_path\")
    end
    subgraph Analysis
        Fraud(\"detect_fraud\")
    end
    Root([Transaction files: CSV/JSON/XML])

    Root --> Load --> Formats
    Load --> Model
    Model --> Fraud
    Fraud --> Findings([Fraud findings])
```

## Prerequisites
- Python 3.11+ (the package uses modern typing and `decimal`/`datetime` utilities)
- `python-dateutil` for ISO timestamp parsing

## Installation
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Upgrade the installer and grab dependencies:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install python-dateutil
   ```

## Running the helpers
Use the loaders and fraud detectors from a short script. Point `load_transactions_from_path` at any supported file (CSV/JSON/XML) or directory of files; it will normalize everything into `Transaction` objects.

```bash
python3 - <<'PY'
from pathlib import Path
from banking_parser import load_transactions_from_path, detect_fraud

root = Path(__file__).resolve().parent
transactions = load_transactions_from_path(root / "demo" / "sample-data.json")
findings = detect_fraud(transactions)
print("Found fraud candidates:", findings)
PY
```

Pass `override_format` to `load_transactions_from_path` when the file extension is missing or inaccurate.

## Testing (optional)
No automated test suite ships with this helper, but you can drop the module into any project with `pytest` or another runner. A quick smoke check is:
```bash
python -m pytest
```
It will fail until you add tests, which is helpful feedback that no regressions are present yet.
