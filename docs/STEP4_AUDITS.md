# Step 4 – Adding Basic Audit Checks

## What we did
- Introduced a new folder `audits/` to keep all audit rules organized.
- Added `audits/basic_checks.py` with three simple checks:
  1. **Security Audit** → always returns PASS
  2. **Performance Audit** → randomly PASS/FAIL
  3. **Data Quality Audit** → randomly PASS/FAIL

- Updated `auditor_agent.py` to:
  - Import `run_basic_audits()`
  - Loop through audit results
  - Send each result to **Slack** and **Notion**

## Expected Output
When running:
```bash
python auditor_agent.py
