# Write Specification

Generate a complete `specification.md` for the AI-powered multi-agent banking pipeline.

## Steps

1. Read `specification-TEMPLATE-hint.md` to understand the required 5-section structure.

2. Read `sample-transactions.json` to understand the 8 input transactions and their edge cases:
   - TXN006: currency "XYZ" (invalid)
   - TXN007: amount "-100.00" (negative)
   - TXN002: amount $25,000 (high value)
   - TXN005: amount $75,000 (very high value)
   - TXN004: timestamp 02:47 UTC, country DE (unusual hour + cross-border)
   - TXN003: amount $9,999.99 (just under $10K threshold)

3. Read `agents/specification_agent.md` to get the full sub-agent instructions, rules, and examples.

4. Generate a complete `specification.md` following the 5-section template:

   **Section 1 — High-Level Objective**: One sentence covering multi-agent, Python, file-based JSON message passing, validation, fraud detection, and settlement.

   **Section 2 — Mid-Level Objectives**: 4–5 concrete, testable requirements derived directly from the sample data edge cases above.

   **Section 3 — Implementation Notes**: Cover `decimal.Decimal` (never float), ISO 4217 whitelist (USD/EUR/GBP/JPY), audit logging format (timestamp + agent + transaction_id + outcome), PII masking (account numbers), file-based JSON messaging, message format with required fields, error handling.

   **Section 4 — Context**: Beginning state (only `sample-transactions.json` exists) → ending state (8 result files in `shared/results/`, ≥ 90% test coverage, README + HOWTORUN complete).

   **Section 5 — Low-Level Tasks**: One entry per pipeline agent (Transaction Validator, Fraud Detector, Settlement Processor), each with Task name, Prompt, File to CREATE, Function to CREATE, and Details.

5. Save the output to `specification.md` in the project root (`homework-6/specification.md`).
