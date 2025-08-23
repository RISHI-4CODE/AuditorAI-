import json

input_path = r"C:\Users\admin\Desktop\AI AUDITOR\harmful-classifier\data\processed\pii-masking-300k\data\test.jsonl"
output_path = r"C:\Users\admin\Desktop\AI AUDITOR\harmful-classifier\data\processed\pii-masking-300k\data\test_preprocessed.jsonl"

severity_map = {
    "NAME": 0,
    "USERNAME": 1,
    "EMAIL": 1,
    "TIME": 0,
    "DATE": 0,
    "ADDRESS": 1,
    "PHONE": 1,
    "SSN": 2,
    "CREDIT_CARD": 2,
    "API_KEY": 2,
    "TOKEN": 2
}

with open(input_path, "r", encoding="utf-8") as fin, \
     open(output_path, "w", encoding="utf-8") as fout:
    for line in fin:
        data = json.loads(line)
        for mask in data.get("privacy_mask", []):
            mask["severity"] = severity_map.get(mask["label"], 0)
        fout.write(json.dumps(data) + "\n")

print("✅ Preprocessed dataset saved to:", output_path)
