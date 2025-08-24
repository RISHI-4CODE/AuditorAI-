🛡️ AI Auditor

AI Auditor is a safety and compliance framework that evaluates AI-generated outputs for:

PII leakage (emails, phone numbers, IDs, etc.)

Toxicity & bias

Hallucinations / unsupported claims

It uses a mix of rule-based regex, trained ML classifiers, and rewriting agents to decide whether an output should PASS, FLAG, or FAIL.

🚀 Features

🔍 Multi-check system – runs PII, bias, and hallucination audits

🤖 Automatic rewrite – unsafe text is rewritten with Gemini

📊 Dashboard – Streamlit UI for interactive demos

🧪 Reproducible experiments – config-driven pipelines with metrics & reports

🏗️ Project Structure
AI AUDITOR
│
├── agent/                   # Entry scripts to run the full auditor pipeline
│   ├── auditor.yaml          # Config file for orchestrating audit checks
│   └── run.py                # Launches auditor agent end-to-end
│
├── app/                     # High-level orchestration layer
│   ├── auditor.py            # Main auditing logic
│   └── auditor_agent.py      # Agent wrapper around auditor for reuse
│
├── audit_service/            # Core audit microservice (stub API)
│   ├── __main__.py           # Run module as script
│   ├── adapters/             # Adapters for external models (e.g., Gemini)
│   ├── audit_checks/         # PII, toxicity, hallucination checks
│   │   └── prompts.py        # Prompt templates for LLM-based checks
│   ├── core.py               # Core orchestration logic
│   ├── main.py               # FastAPI entrypoint (stubbed for now)
│   ├── models/               # Stored ML models
│   │   └── toxicity_and_biasness/
│   │       ├── logistic.pkl
│   │       └── tfidf_vectorizer.pkl
│   ├── models.py             # Pydantic schemas for requests/responses
│   ├── routers/              # API route handlers (audit endpoints)
│   ├── services/             # Service clients (PII, toxicity, rewrite)
│   └── storage/              # In-memory or file-based logging
│
├── dashboard/                # Streamlit dashboard
│   └── app.py                 # Visual UI for audits
│
│
├── harmful-classifier/       # ML classifier development
│   ├── data/                  # Datasets for training & testing
│   │   └── processed/          # Cleaned versions of datasets
│   ├── models/                # Saved models (e.g., PII logistic regression)
│   ├── reports/               # Training reports, metrics, confusion matrices
│   ├── src/                   # Source code for training pipelines
│   │   ├── config.yaml         # Config (thresholds, paths)
│   │   ├── features/           # Feature engineering (regex, TF-IDF, etc.)
│   │   ├── models/             # Model inference & analysis
│   │   └── pipeline/           # Service wrapper (FastAPI stub)
│   └── tests/                 # Unit tests
│
├── integrations/             # (Optional) Integrations (Notion/Slack stubs)
│
├── pyproject.toml            # Project metadata + scripts
├── readme.md                 # (You are here 🚀)
├── reports/                  # Extra analysis outputs
└── requirements.txt          # Python dependencies

⚡ Quickstart
1. Setup
git clone https://github.com/your-repo/ai-auditor.git
cd ai-auditor
pip install -r requirements.txt

2. Run Auditor
python agent/run.py --config agent/auditor.yaml

3. Launch Dashboard
streamlit run dashboard/app.py

📊 Example Output

Input:

Call me at 9876543210 tomorrow.


Audit Result:

{
  "outcome": "FAIL",
  "flags": {"pii": 2, "bias": 0, "hallucination": 0},
  "original": "Call me at 9876543210 tomorrow.",
  "cleaned": "Call me tomorrow at [redacted]."
}

🎯 Why It Matters

Ensures responsible AI usage in real-world systems

Prevents PII leaks and unsafe outputs

Provides transparent PASS/FLAG/FAIL audit trail

Easily extensible with new models & datasets

Demo-ready (dashboard)

Tackles AI safety, a top concern for enterprises

Research-backed with ML, not just LLM prompts

Balanced between practicality and innovation