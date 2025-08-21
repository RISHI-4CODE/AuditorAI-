import os
import google.generativeai as genai
from datetime import datetime

def run_ai_audits_on_code(directory="project_code"):
    results = []
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Walk through files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # scan Python files
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    code = f.read()

                # Send code to Gemini
                prompt = f"""
                You are an AI code auditor. Analyze the following Python code:
                {code}

                Provide:
                - Security risks
                - Performance issues
                - Data quality concerns
                - Overall PASS/FAIL decision
                """
                response = model.generate_content(prompt)
                text = response.text.strip()

                # Simple pass/fail detection
                status = "PASS" if "PASS" in text.upper() else "FAIL"

                results.append({
                    "task": f"AI Audit on {file}",
                    "status": status,
                    "details": text,
                    "timestamp": datetime.utcnow().isoformat()
                })

    return results
