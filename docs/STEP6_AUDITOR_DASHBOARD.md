# 📊 AI Auditor Dashboard

This module provides a **real-time dashboard** for monitoring audits performed by the AuditorAgent.  
It connects to **Notion** for persistent storage and uses **Streamlit** for live visualization.

---

## 🚀 Features
- Fetches audit logs from **Notion Database**
- Displays **Task, Status, Timestamp, Details**
- Color-coded status indicators (✅ PASS / ❌ FAIL)
- Debug mode to check actual Notion property mappings
- Works seamlessly with **Slack + Notion logging pipeline**

---

## 📂 File Overview
- `dashboard.py` → Streamlit dashboard
- `auditor_agent.py` → Runs audits + logs results
- `notion_utils.py` (optional) → Helper for Notion queries

---

## 🔧 Setup
1. Install dependencies:
   ```bash
   pip install streamlit pandas python-dotenv notion-client
