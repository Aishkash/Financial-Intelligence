import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib

DATA_PATH = "data/processed/transactions_with_features.csv"

df = pd.read_csv(DATA_PATH)

FEATURES = [
    "hour",
    "day_of_week",
    "time_since_last_txn",
    "amount_zscore",
    "user_avg_amount",
    "user_std_amount"
]

TARGET = "is_fraud"

X = df[FEATURES]
y = df[TARGET]

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=50,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_val)
y_prob = model.predict_proba(X_val)[:, 1]

print(classification_report(y_val, y_pred))
print("ROC AUC:", roc_auc_score(y_val, y_prob))

joblib.dump(model, "backend/app/models/risk_model.pkl")
print("Model saved.")