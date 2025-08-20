# Step 5 – AI-Powered Audits with Gemini

## What We Did
- Installed and configured **Google Gemini** via `google-generativeai`
- Added a new audit module: `audits/ai_audits.py`
- Integrated Gemini into `auditor_agent.py`
- Now our agent performs **static + AI-powered audits**

## How It Works
- Sends a code snippet to Gemini
- Gemini returns feedback (security, performance, data quality insights)
- Extracts `PASS/FAIL` from response
- Logs results to:
  - ✅ Slack (team updates)
  - ✅ Notion (audit history)

## Example Output
