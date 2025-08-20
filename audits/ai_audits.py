import os
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def run_ai_audit(code_snippet: str):
    """
    Send code/data to Gemini and get an AI-powered audit result.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        You are an AI Auditor. Review the following code snippet and
        point out any security, performance, or data quality issues.

        Code:
        {code_snippet}

        Respond in format:
        - Verdict: PASS/FAIL
        - Details: short explanation
        """
        response = model.generate_content(prompt)

        text = response.text.strip()

        # Extract PASS/FAIL
        status = "PASS" if "PASS" in text.upper() else "FAIL"
        return {"task": "AI Audit", "status": status, "details": text}

    except Exception as e:
        return {"task": "AI Audit", "status": "FAIL", "details": f"Error: {e}"}
