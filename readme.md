# AuditorAgent 🕵️‍♂️

AI-powered agent that audits code & workflows, then logs findings to Notion and sends alerts to Slack.

---

## ✅ Setup Steps Done So Far

### 1. Slack Setup
- Created Slack app with Bot permissions
- Installed app to workspace
- Saved `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` in `.env`

### 2. Notion Setup
- Created `Audit Logs` database in Notion
- Added properties: Task, Status, Timestamp, Details
- Created integration + saved `NOTION_API_KEY` and `NOTION_DATABASE_ID` in `.env`
- Tested connection with `test_notion.py`

### 3. Git Setup
- Initialized repo with `.gitignore`
- Added README.md
- First commit done 🚀

---

## 🔮 Next Steps
- Build core `auditor_agent.py` that integrates Slack + Notion
- Add modular audit functions (code quality, security, etc.)
- Demo-ready workflow for hackathon
