from sklearn.ensemble import RandomForestClassifier
import numpy as np

class RiskModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )

    def train(self, X, y):
        self.model.fit(X, y)

    def predict_risk(self, X):
        return self.model.predict_proba(X)[:, 1]