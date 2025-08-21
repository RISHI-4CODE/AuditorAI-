📝 Step 7 – Bias & Toxicity Detection

In this step, we introduced the Bias and Toxicity Detection audit.
This module expands the AuditorAgent’s capabilities by scanning text for biased or toxic language.

🚀 Features Implemented

Added bias_detector.py

Maintains a small lexicon of toxic/biased words.

Detects occurrences in audit text.

Returns structured findings in JSON format.

Includes a summary helper (summarize_bias) for concise logging.

📂 File Overview

bias_detector.py → Implements bias/toxicity scan logic.

Integrated with auditor.py (will orchestrate checks in the next step).