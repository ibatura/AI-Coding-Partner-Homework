Run the multi-agent banking pipeline end-to-end.

## Steps

1. **Check prerequisites**: Verify that `sample-transactions.json` exists in the project root (`homework-6/`). If it is missing, stop and report an error — do not proceed.

2. **Clear shared/ directories**: Remove all files from `shared/input/`, `shared/processing/`, `shared/output/`, and `shared/results/` to ensure a clean run. Create the directories if they do not exist.

3. **Run the pipeline**: Execute the following command from the project root:
   ```
   python3 integrator.py
   ```
   Capture and display the output as it runs.

4. **Show results summary**: After the pipeline completes, read `shared/results/pipeline_summary.json` and display:
   - Total transactions processed
   - Settled count
   - Settled with review count
   - Held for review count
   - Rejected count
   - Total fees collected
   - Total volume processed

5. **Report rejected transactions**: For each `*_rejected.json` file in `shared/results/`, show:
   - Transaction ID
   - Rejection reason

Format the summary as a readable table or structured list.
