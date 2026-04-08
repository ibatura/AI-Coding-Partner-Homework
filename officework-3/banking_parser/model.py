from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

from dateutil import parser as dateutil_parser


@dataclass(frozen=True)
class Transaction:
    """Normalized representation of a banking transaction."""

    id: str
    timestamp: datetime
    account_id: str
    type: str
    amount: Decimal
    currency: str
    counterparty: str
    country: str
    description: str
    account_home_country: str
    source_path: str = field(default="")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "account_id": self.account_id,
            "type": self.type,
            "amount": str(self.amount),
            "currency": self.currency,
            "counterparty": self.counterparty,
            "country": self.country,
            "description": self.description,
            "account_home_country": self.account_home_country,
            "source_path": self.source_path,
        }

    @staticmethod
    def from_mapping(data: Dict[str, Any], source_path: str = "") -> "Transaction":
        def get(key: str, default: str = "") -> str:
            value = data.get(key)
            if value is None:
                return default
            return str(value).strip()

        amount_str = data.get("amount") or data.get("Amount")
        if amount_str is None:
            raise ValueError("missing amount")
        try:
            amount = Decimal(str(amount_str))
        except InvalidOperation as exc:
            raise ValueError("invalid amount") from exc

        timestamp_raw = data.get("timestamp") or data.get("Timestamp")
        if not timestamp_raw:
            raise ValueError("missing timestamp")
        timestamp = dateutil_parser.isoparse(str(timestamp_raw))

        return Transaction(
            id=get("id"),
            timestamp=timestamp,
            account_id=get("account_id"),
            type=get("type", "transfer"),
            amount=amount,
            currency=get("currency", "USD"),
            counterparty=get("counterparty", ""),
            country=get("country", "US"),
            description=get("description", ""),
            account_home_country=get("account_home_country", get("home_country", "US")),
            source_path=source_path,
        )
