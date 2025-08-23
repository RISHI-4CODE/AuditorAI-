from src.features.pii_regex import pii_indicators, contains_high_severity_pii
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from src.features.pii_regex import pii_indicators

class PiiFeatureBuilder:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)

    def fit(self, texts):
        return self.vectorizer.fit(texts)

    def transform(self, texts):
        tfidf = self.vectorizer.transform(texts)

        regex_features = []
        for t in texts:
            matches = pii_indicators(t)
            regex_features.append([int(matches["email"]),
                                   int(matches["phone"]),
                                   int(matches["ssn"]),
                                   int(matches["credit_card"])])
        regex_features = np.array(regex_features)

        return np.hstack([tfidf.toarray(), regex_features])
