from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, List

from .model import Transaction

SUPPORTED_FORMATS = {"csv", "json", "xml"}


def load_transactions_from_path(path: Path | str, override_format: str | None = None) -> List[Transaction]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if not path.is_file():
        raise ValueError(f"{path} is not a file")

    file_format = _resolve_format(path, override_format)
    parser = {
        "csv": _parse_csv,
        "json": _parse_json,
        "xml": _parse_xml,
    }[file_format]
    return parser(path)


def gather_transaction_files(path: Path | str, extensions: Iterable[str] | None = None) -> List[Path]:
    path = Path(path)
    extensions = {ext.lower() for ext in (extensions or SUPPORTED_FORMATS)}
    if path.is_file():
        if path.suffix.lstrip(".").lower() in extensions:
            return [path]
        return []
    files: List[Path] = []
    for ext in extensions:
        files.extend(path.rglob(f"*.{ext}"))
    return sorted(files)


def _resolve_format(path: Path, override_format: str | None) -> str:
    if override_format:
        candidate = override_format.lower()
        if candidate not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {override_format}")
        return candidate
    suffix = path.suffix.lstrip(".").lower()
    if suffix in SUPPORTED_FORMATS:
        return suffix
    raise ValueError(f"Could not infer format from {path}")


def _parse_csv(path: Path) -> List[Transaction]:
    transactions: List[Transaction] = []
    with path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not row:
                continue
            transactions.append(Transaction.from_mapping(row, str(path)))
    return transactions


def _parse_json(path: Path) -> List[Transaction]:
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)
    if isinstance(payload, dict):
        payload = payload.get("transactions", [])
    if not isinstance(payload, list):
        raise ValueError("JSON payload must be a list of transactions")
    return [Transaction.from_mapping(entry, str(path)) for entry in payload]


def _parse_xml(path: Path) -> List[Transaction]:
    tree = ET.parse(path)
    root = tree.getroot()
    transactions: List[Transaction] = []
    for element in root.findall(".//transaction"):
        mapping = {child.tag: child.text or "" for child in element}
        transactions.append(Transaction.from_mapping(mapping, str(path)))
    return transactions
