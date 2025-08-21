# 🛡️ AI Auditor

An **AI-powered auditing service** that analyzes generated text for **risks, bias, hallucinations, PII, and harmful content**.  
It automatically **reworks unsafe outputs**, logs findings, and stores high-risk cases for future training.

---

## ✨ Features
- 🔍 **PII Detection** – scans text for sensitive data (emails, phone numbers, credit cards, API keys, Aadhaar, IPs).  
- ⚖️ **Risk Scoring** – assigns a score (0–100) based on PII, toxicity, hallucination, and logistic harm model.  
- 🛑 **Auto-Redo** – rewrites unsafe outputs into safer alternatives.  
- 📊 **Tiered Risk Levels** – `low`, `medium`, `high` with thresholds.  
- 🗃️ **Memory Log + SQLite Storage** – track all audits for debugging & history.  
- 📝 **Notion Logging** – high-risk cases logged into Notion DB for analysis.  
- 🚫 **Slack Alerts** (optional, deprecated by roadmap).  

---

## ⚡ Quickstart

### 1️⃣ Clone & Install
```bash
git clone <your-repo-url>
cd ai-auditor
pip install -r requirements.txt
