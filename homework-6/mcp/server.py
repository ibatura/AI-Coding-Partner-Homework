from fastmcp import FastMCP
import json
from pathlib import Path

mcp = FastMCP("pipeline-status")

RESULTS_DIR = Path(__file__).parent.parent / "shared" / "results"


@mcp.tool()
def get_transaction_status(transaction_id: str) -> str:
    """Get the current status of a transaction by ID."""
    for suffix in ("_result.json", "_rejected.json"):
        path = RESULTS_DIR / f"{transaction_id}{suffix}"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                return json.dumps(data.get("data", data), indent=2)
            except (json.JSONDecodeError, OSError) as exc:
                return json.dumps({"error": f"Failed to read result: {exc}", "transaction_id": transaction_id})
    return json.dumps({"error": "Transaction not found", "transaction_id": transaction_id})


@mcp.tool()
def list_pipeline_results() -> str:
    """List a summary of all processed transactions."""
    summaries = []
    counts = {"total": 0, "settled": 0, "settled_with_review": 0, "held_for_review": 0, "rejected": 0}

    for path in sorted(RESULTS_DIR.glob("TXN*.json")):
        try:
            raw = json.loads(path.read_text())
            data = raw.get("data", raw)
            status = data.get("settlement_status") or data.get("status", "unknown")
            summaries.append({
                "transaction_id": data.get("transaction_id"),
                "status": status,
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "risk_level": data.get("fraud_risk_level"),
            })
            counts["total"] += 1
            if status in counts:
                counts[status] += 1
        except (json.JSONDecodeError, OSError):
            continue

    return json.dumps({"transactions": summaries, "counts": counts}, indent=2)


@mcp.tool()
def get_pipeline_stats() -> str:
    """Get aggregate counts by settlement status."""
    counts = {"total": 0, "settled": 0, "settled_with_review": 0, "held_for_review": 0, "rejected": 0}
    total_fees = 0.0
    total_volume = 0.0

    for path in sorted(RESULTS_DIR.glob("TXN*.json")):
        try:
            raw = json.loads(path.read_text())
            data = raw.get("data", raw)
            status = data.get("settlement_status") or data.get("status", "unknown")
            counts["total"] += 1
            if status in counts:
                counts[status] += 1
            try:
                total_fees += float(data.get("fee_amount", 0))
            except (ValueError, TypeError):
                pass
            try:
                total_volume += float(data.get("amount", 0))
            except (ValueError, TypeError):
                pass
        except (json.JSONDecodeError, OSError):
            continue

    counts["total_fees"] = f"${total_fees:,.2f}"
    counts["total_volume"] = f"${total_volume:,.2f}"
    return json.dumps(counts, indent=2)


@mcp.resource("pipeline://summary")
def pipeline_summary() -> str:
    """Get the latest pipeline run summary."""
    summary_path = RESULTS_DIR / "pipeline_summary.json"
    if not summary_path.exists():
        return "No pipeline run found. Run the pipeline first."

    try:
        s = json.loads(summary_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return f"Error reading pipeline summary: {exc}"

    def fmt_money(value: str) -> str:
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return str(value)

    lines = [
        "Pipeline Run Summary",
        "====================",
        f"Run ID: {s.get('run_id', 'N/A')}",
        f"Completed: {s.get('completed_at', 'N/A')}",
        f"Total Transactions: {s.get('total_transactions', 0)}",
        f"Settled: {s.get('settled', 0)}",
        f"Settled with Review: {s.get('settled_with_review', 0)}",
        f"Held for Review: {s.get('held_for_review', 0)}",
        f"Rejected: {s.get('rejected', 0)}",
        f"Total Fees: {fmt_money(s.get('total_fees_collected', '0'))}",
        f"Total Volume: {fmt_money(s.get('total_volume_processed', '0'))}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()