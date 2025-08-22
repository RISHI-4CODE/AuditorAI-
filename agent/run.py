# agent/run.py
"""
Entrypoint to run the AuditorAgent defined in auditor.yaml.
This script simulates both:
1. User input being checked before sending to the AI.
2. AI output being checked and retried up to 3 times if unsafe.
"""

from portia import Agent

if __name__ == "__main__":
    # Load Portia agent from YAML workflow
    auditor = Agent.load("agent/auditor.yaml")

    # === Example 1: User Input check ===
    user_input = "Contact me at john@acme.com. My token is sk_1234567890abcdefghijklmnop."
    result_input = auditor.run({"doc": user_input, "mode": "input"})
    print("\n=== User Input Check ===")
    print("Original:", user_input)
    print("Verdict:", result_input["verdict"])
    print("Cleaned:", result_input["clean_doc"])

    # === Example 2: AI Output check ===
    ai_output = "The secret key for the system is sk_abcdef123456. Also, people from XYZ group are bad."
    result_output = auditor.run({"doc": ai_output, "mode": "output"})
    print("\n=== AI Output Check ===")
    print("Original:", ai_output)
    print("Verdict:", result_output["verdict"])
    print("Cleaned:", result_output["clean_doc"])
