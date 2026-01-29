import pandas as pd

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("timestamp")

    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.dayofweek

    df["time_since_last_txn"] = (
        df.groupby("user_id")["timestamp"]
        .diff()
        .dt.total_seconds()
        .fillna(0)
    )

    user_stats = df.groupby("user_id")["amount"].agg(["mean", "std"]).reset_index()
    user_stats.columns = ["user_id", "user_avg_amount", "user_std_amount"]

    df = df.merge(user_stats, on="user_id", how="left")

    df["amount_deviation"] = (
        df["amount"] - df["user_avg_amount"]
    ) / (df["user_std_amount"] + 1)

    return df