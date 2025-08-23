import pandas as pd
from sklearn.model_selection import train_test_split

def load_toxigen_data(path: str):
    """
    Load toxigen dataset and map into:
    0 = PASS
    1 = FLAG (bias / subtle toxicity)
    2 = FAIL (strong toxicity)
    """
    df = pd.read_csv(path)

    def map_label(row):
        if row["prompt_label"] == 0:
            return 0  # PASS
        elif row["prompt_label"] == 1 and row["roberta_prediction"] < 0.5:
            return 1  # FLAG
        else:
            return 2  # FAIL

    df["class"] = df.apply(map_label, axis=1)

    return train_test_split(
        df["generation"],  # <- use model-generated text
        df["class"],
        test_size=0.2,
        random_state=42
    )
