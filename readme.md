🛡️ AI Auditor

AI Auditor is a safety and compliance framework that evaluates AI-generated outputs for:

PII leakage (emails, phone numbers, IDs, etc.)

Toxicity & bias

Hallucinations / unsupported claims

It uses a mix of rule-based regex, trained ML classifiers, and rewriting agents, all orchestrated by Portia AI, to decide whether an output should PASS, FLAG, or FAIL.

🚀 Features

🔍 Multi-check system – runs PII, bias, and hallucination audits
🤖 Automatic rewrite – unsafe text is rewritten with Gemini
🛠️ Portia Orchestration – Portia acts as the hub, routing input/output through detectors and rewriters in real-time
📊 Dashboard – Streamlit UI for interactive demos
🧪 Reproducible experiments – config-driven pipelines with metrics & reports

🕸️ How Portia Connects Everything

Portia AI is the central orchestrator of the pipeline:

User Input
   │
   ▼
[Portia] → Input Audit  
   ├── PII Detector (regex/rules)  
   ├── Toxicity & Bias Classifier (ML)  
   └── Policy Guard (prompt injection / unsafe intent)  

   │
   ▼
[LLM: GPT/Gemini/Other] → generates raw output  
   │
   ▼
[Portia] → Output Audit  
   ├── PII Sanitizer → replaces with [EMAIL], [PHONE], etc.  
   ├── Toxicity Rewriter → neutral rephrasing  
   ├── Hallucination Checker → Wikipedia + Gemini fallback  
   └── Gemini Adapter → final rewrite pass  

   │
   ▼
Safe Output (PASS/FLAG/FAIL + cleaned text)


Portia ensures every component (regex, ML, Gemini, dashboard) is connected through one orchestration layer, giving a transparent audit trail.

🏗️ Project Structure
AI AUDITOR

│

├── agent/              # Entry scripts (Portia-driven pipelines)

│   ├── auditor.yaml    # Config file (Portia orchestrator)

│   └── run.py          # Launches end-to-end auditor via Portia


│

├── app/                # High-level orchestration layer

│   ├── auditor.py      # Main auditing logic (Portia orchestrated)

│   └── auditor_agent.py# Agent wrapper (Portia-powered)

│

├── audit_service/      # Core audit microservice

│   ├── adapters/       # Gemini + Portia adapters

│   ├── audit_checks/   # PII, toxicity, hallucination checks

│   ├── core.py         # Orchestration glue with Portia

│   ├── models/         # ML classifiers (toxicity, bias)

│   ├── routers/        # API endpoints for audits

│   └── services/       # Portia service clients

│

├── dashboard/          # Streamlit dashboard (queries via Portia)

│

├── harmful-classifier/ # ML model training

│

└── ...


⚡ Quickstart
git clone https://github.com/your-repo/ai-auditor.git
cd ai-auditor
pip install -r requirements.txt


Run full auditor (via Portia):

python agent/run.py --config agent/auditor.yaml


Launch dashboard:

streamlit run dashboard/app.py

📊 Example Output

Input:

Call me at 9876543210 tomorrow.


Audit Result:

{
  "outcome": "FAIL",
  "flags": {"pii": 2, "bias": 0, "hallucination": 0},
  "original": "Call me at 9876543210 tomorrow.",
  "cleaned": "Call me tomorrow at [PHONE].",
  "orchestrator": "Portia AI"
}

🎯 Why It Matters

Ensures responsible AI usage in real-world systems

Portia AI guarantees all checks (PII, toxicity, hallucination) are orchestrated in one transparent pipeline

Prevents leaks, unsafe outputs, and bias at scale

Provides PASS/FLAG/FAIL audit trail with Portia-managed logs

Extensible with new checks, models, and adapters

Demo-ready dashboard
