# agent/run.py
from portia import Agent

if __name__ == "__main__":
    # Load Portia agent from YAML workflow
    auditor = Agent.load("agent/auditor.yaml")

    # Example input
    doc = "Contact me at john@acme.com. My token is sk_1234567890abcdefghijklmnop."

    # Run through the audit pipeline
    result = auditor.run({"doc": doc})

    # Print final cleaned output
    print("=== Final Audited Output ===")
    print(result["clean_doc"])
