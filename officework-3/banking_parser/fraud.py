from __future__ import annotations

from collections import defaultdict, deque
from datetime import timedelta
from decimal import Decimal
from typing import Iterable, List

from .model import Transaction

LARGE_TRANSACTION_THRESHOLD = 10000
RAPID_BURST_COUNT = 3
RAPID_BURST_WINDOW = timedelta(minutes=2)
SPLIT_PAYMENT_WINDOW = timedelta(minutes=10)
SPLIT_PAYMENT_THRESHOLD = 10000
ROUND_AMOUNT_THRESHOLD = 1000


def detect_fraud(transactions: Iterable[Transaction]) -> List[dict]:
    ordered = sorted(transactions, key=lambda tx: tx.timestamp)
    findings: List[dict] = []
    findings.extend(_find_large_transactions(ordered))
    findings.extend(_find_rapid_bursts(ordered))
    findings.extend(_find_split_payments(ordered))
    findings.extend(_find_round_amounts(ordered))
    findings.extend(_find_foreign_activity(ordered))
    return findings


def _find_large_transactions(transactions: List[Transaction]) -> List[dict]:
    return [
        _make_finding(
            "large_transaction",
            [tx.id],
            {"amount": str(tx.amount), "threshold": LARGE_TRANSACTION_THRESHOLD},
        )
        for tx in transactions
        if tx.amount > LARGE_TRANSACTION_THRESHOLD
    ]


def _find_rapid_bursts(transactions: List[Transaction]) -> List[dict]:
    results = []
    by_account = defaultdict(list)
    for tx in transactions:
        by_account[tx.account_id].append(tx)
    for account, txs in by_account.items():
        window = deque()
        for tx in txs:
            window.append(tx)
            while window and tx.timestamp - window[0].timestamp > RAPID_BURST_WINDOW:
                window.popleft()
            if len(window) >= RAPID_BURST_COUNT:
                results.append(
                    _make_finding(
                        "rapid_burst",
                        [entry.id for entry in list(window)],
                        {"account_id": account, "count": len(window)},
                    )
                )
                window.popleft()
    return results


def _find_split_payments(transactions: List[Transaction]) -> List[dict]:
    results = []
    grouped = defaultdict(list)
    for tx in transactions:
        grouped[(tx.account_id, tx.counterparty)].append(tx)
    for (account, counterparty), txs in grouped.items():
        start = 0
        total = Decimal("0")
        running: List[Transaction] = []
        for tx in txs:
            running.append(tx)
            total += tx.amount
            while running and tx.timestamp - running[0].timestamp > SPLIT_PAYMENT_WINDOW:
                total -= running[0].amount
                running.pop(0)
            if len(running) >= 3 and total > SPLIT_PAYMENT_THRESHOLD:
                results.append(
                    _make_finding(
                        "split_payment",
                        [entry.id for entry in running],
                        {
                            "account_id": account,
                            "counterparty": counterparty,
                            "total": str(total),
                        },
                    )
                )
    return results


def _find_round_amounts(transactions: List[Transaction]) -> List[dict]:
    results = []
    for tx in transactions:
        if tx.amount >= ROUND_AMOUNT_THRESHOLD and tx.amount % 100 == 0:
            results.append(
                _make_finding(
                    "round_amount",
                    [tx.id],
                    {"amount": str(tx.amount)},
                )
            )
    return results


def _find_foreign_activity(transactions: List[Transaction]) -> List[dict]:
    results = []
    for tx in transactions:
        if tx.country and tx.account_home_country and tx.country != tx.account_home_country:
            results.append(
                _make_finding(
                    "foreign_activity",
                    [tx.id],
                    {
                        "country": tx.country,
                        "account_home_country": tx.account_home_country,
                    },
                )
            )
    return results


def _make_finding(rule: str, transaction_ids: List[str], details: dict) -> dict:
    return {
        "rule": rule,
        "transaction_ids": transaction_ids,
        "details": details,
    }
