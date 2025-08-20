from portia import Agent

# ensure PORTIA creds are exported if needed
auditor = Agent.load("agent/auditor.yaml")

# Example run:
if __name__ == "__main__":
    doc = "Contact me at john@acme.com. My token is sk_1234567890abcdefghijklmnop."
    result = auditor.run({"doc": doc})
    print(result)
