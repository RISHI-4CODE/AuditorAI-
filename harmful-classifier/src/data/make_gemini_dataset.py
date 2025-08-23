import os
import time
import pandas as pd
from tqdm import tqdm
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file!")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# ==== CONFIG ====
REQUESTS_PER_MINUTE = 15  # Free tier limit for gemini-2.0-flash
DELAY = 60 / REQUESTS_PER_MINUTE
TOTAL_ROWS = 6000
ROWS_PER_REQUEST = 5   # because each prompt generates 5 queries
# =================
def save_partial(samples, out_path="harmful-classifier/data/processed/partial_dataset.csv"):
    import pandas as pd, os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df = pd.DataFrame(samples)
    df.to_csv(out_path, index=False)
    print(f"💾 Autosaved {len(df)} rows → {out_path}")

def generate_examples(prompt, n=100, samples=None, label=None, save_every=20):
    """Generate n samples using Gemini for a given class prompt"""
    data = []
    for i in tqdm(range(n)):
        try:
            resp = model.generate_content(prompt)
            if resp and resp.text:
                lines = [l.strip() for l in resp.text.split("\n") if l.strip()]
                data.extend(lines)
                
                # Add to samples dict if provided
                if samples is not None and label is not None:
                    samples["text"].extend(lines)
                    samples["label"].extend([label] * len(lines))
                    
                    # 🔑 Autosave every X steps
                    if i % save_every == 0 and i > 0:
                        save_partial(samples)
        except Exception as e:
            print(f"⚠️ Error: {e}")
    return data




def main():
    samples = {"text": [], "label": []}

    # Prompts
    benign_prompts = [
        "Generate 5 harmless user queries like trivia, jokes, or creative requests.",
    ]
    pii_prompts = [
        "Generate 5 user queries with PII (fake names, phone numbers, emails, addresses).",
    ]
    harmful_prompts = [
        "Generate 5 unsafe or toxic user queries (insults, hate speech, illegal requests).",
    ]

    all_prompts = [(benign_prompts, 0), (pii_prompts, 1), (harmful_prompts, 2)]

    for prompts, label in all_prompts:
        for p in prompts:
            needed_batches = TOTAL_ROWS // (ROWS_PER_REQUEST * len(all_prompts))
            texts = generate_examples(p, n=needed_batches)
            samples["text"].extend(texts)
            samples["label"].extend([label] * len(texts))

    # Save dataset
    df = pd.DataFrame(samples)
    os.makedirs("harmful-classifier/data/processed", exist_ok=True)
    out_path = "harmful-classifier/data/processed/personalized_dataset.csv"
    df.to_csv(out_path, index=False)
    print(f"✅ Saved dataset with {len(df)} rows → {out_path}")


if __name__ == "__main__":
    main()
