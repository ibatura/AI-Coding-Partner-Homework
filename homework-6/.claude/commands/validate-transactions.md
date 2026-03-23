Validate all transactions in sample-transactions.json without processing them (dry-run mode).

## Steps

1. **Run the validator in dry-run mode**: Execute the following command from the project root:
   ```
   python3 agents/transaction_validator.py --dry-run --sample sample-transactions.json
   ```
   This validates all transactions without writing any files to `shared/` directories.

2. **Report results**: Display:
   - Total transaction count
   - Valid count
   - Invalid count

3. **Show as table**: Format all transactions as a table with columns:
   - TXN ID
   - Amount
   - Currency
   - Result (✅ validated / ❌ rejected)
   - Rejection reason (if applicable)

4. **Highlight issues**: Call out each invalid transaction with its ID and reason so the user can take corrective action.
