# Research Notes — context7 Queries During Pipeline Code Generation

These queries were performed via the context7 MCP server while the Code Generation sub-agent
(`agents/code_generation_agent.md`) was used to generate the banking pipeline code.

---

## Query 1: Python Decimal Module

- **Search**: `python decimal module monetary arithmetic`
- **context7 library ID**: `/python/cpython` (Python standard library — `decimal` module)
- **Key insight 1 — Always use the string constructor**:
  `Decimal("0.001")` is safe; `Decimal(0.001)` silently captures the floating-point approximation
  `0.001000000000000000020816681711721685228...` and introduces rounding errors in monetary math.
  All amount literals in the pipeline use string form: `Decimal("0.001")`, `Decimal("50.00")`, etc.
- **Key insight 2 — `quantize` + `ROUND_HALF_UP` for money**:
  `amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` rounds to 2 decimal places using
  banker-safe half-up rounding, which matches standard financial rounding rules.
- **Key insight 3 — Avoid arithmetic with mixed types**:
  Never mix `Decimal` with `float` in expressions. `Decimal("1500.00") * 0.001` raises
  `TypeError`. Always write `Decimal("1500.00") * Decimal("0.001")`.
- **Applied in**:
  - `agents/base_agent.py` — `mask_pii` avoids numeric conversion entirely
  - `agents/transaction_validator.py` — `Decimal(str(data["amount"]))` wraps raw string safely
  - `agents/settlement_processor.py` — `_calculate_fee()`, `net_amount` calculation, all
    Decimal constants defined as module-level `Decimal("...")` literals

---

## Query 2: Python Logging — Structured Audit Trail

- **Search**: `python logging module structured format audit trail`
- **context7 library ID**: `/python/cpython` (Python standard library — `logging` module)
- **Key insight 1 — Use `logging.getLogger(name)` per agent, not `logging.basicConfig`**:
  Each agent configures its own named logger (`logging.getLogger(self.name)`). This lets log
  records carry the agent name automatically in every line, enabling per-agent log filtering
  in production. `basicConfig` at module level would create a single root logger shared across
  all agents, losing per-agent identity.
- **Key insight 2 — Guard against duplicate handlers**:
  When the same Python process instantiates multiple agent objects (as the integrator does),
  `getLogger(name)` returns the same logger instance each time. Without `if not logger.handlers`,
  each new instantiation adds another `StreamHandler`, causing duplicate log lines. The guard
  in `BaseAgent.setup_logging()` prevents this.
- **Key insight 3 — `logging.WARNING` for anomalous events**:
  HIGH-risk transactions and held settlements log at `WARNING` level rather than `INFO` so that
  monitoring systems can filter on level without parsing message content. All agents follow this
  pattern: normal outcomes → `INFO`, security-relevant outcomes → `WARNING`.
- **Applied in**:
  - `agents/base_agent.py` — `setup_logging()` method: named logger, guarded handler, structured
    format string `"%(asctime)s | %(name)s | %(levelname)s | %(message)s"`
  - `agents/fraud_detector.py` — `WARNING` for HIGH risk scores
  - `agents/settlement_processor.py` — `WARNING` for `held_for_review` outcomes

---

## Query 3: Python `pathlib` — File-Based Messaging

- **Search**: `python pathlib file operations cross-platform`
- **context7 library ID**: `/python/cpython` (Python standard library — `pathlib` module)
- **Key insight — `Path` objects compose safely across OS**:
  `Path("shared/output") / f"{transaction_id}_validated.json"` uses `/` operator for path
  composition, which handles Windows `\` vs Unix `/` transparently. `str(path)` converts back
  for `open()`. Using `Path.mkdir(parents=True, exist_ok=True)` avoids race conditions when
  multiple agents create directories concurrently.
- **Applied in**:
  - All three pipeline agents (`transaction_validator.py`, `fraud_detector.py`,
    `settlement_processor.py`) and `integrator.py` — all file paths use `Path(...)` composition
    rather than string concatenation

---

## Query 4: Python `uuid` Module — Message ID Generation

- **Search**: `python uuid4 unique identifier generation`
- **context7 library ID**: `/python/cpython` (Python standard library — `uuid` module)
- **Key insight — `uuid.uuid4()` for random, collision-safe IDs**:
  `uuid4()` generates a 128-bit random UUID with ~5.3 × 10³⁶ possible values, making accidental
  collisions negligible for a pipeline processing thousands of transactions per day. The result is
  converted to string with `str(uuid.uuid4())` for JSON serialisation. For settlement IDs the
  first 8 hex characters (`str(uuid.uuid4())[:8]`) provide a short human-readable reference
  (`STL-xxxxxxxx`) while retaining enough entropy for operational use.
- **Applied in**:
  - `agents/base_agent.py` — `create_message_envelope()` sets `message_id`
  - `agents/settlement_processor.py` — `settlement_id = f"STL-{str(uuid.uuid4())[:8]}"`
  - `integrator.py` — each input envelope gets its own `message_id`
