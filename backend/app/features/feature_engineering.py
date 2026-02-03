import pandas as pd
import numpy as np


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering for user-relative fraud detection.

    Input columns required:
    - transaction_type
    - user_id
    - amount
    - timestamp
    - device_id
    - location

    Output:
    - Original columns + engineered features
    """

    df = df.copy()

    # ----------------------------
    # 1. Timestamp handling
    # ----------------------------
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if df["timestamp"].isna().any():
        raise ValueError("Invalid timestamp detected")

    df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

    # Basic time features
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    # ----------------------------
    # 2. Velocity abuse
    # ----------------------------
    df["time_since_last_txn"] = (
        df.groupby("user_id")["timestamp"]
        .diff()
        .dt.total_seconds()
        .fillna(0)
    )

    df["rapid_txn"] = (df["time_since_last_txn"] < 300).astype(int)

    # ----------------------------
    # 3. Amount anomalies (user-relative)
    # ----------------------------
    user_amount_stats = (
        df.groupby("user_id")["amount"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={
            "mean": "user_avg_amount",
            "std": "user_std_amount"
        })
    )

    df = df.merge(user_amount_stats, on="user_id", how="left")

    # Avoid divide-by-zero
    df["user_std_amount"] = df["user_std_amount"].fillna(0) + 1

    df["amount_zscore"] = (
        (df["amount"] - df["user_avg_amount"]) / df["user_std_amount"]
    )

    df["is_large_amount"] = (df["amount_zscore"] > 3).astype(int)

    # ----------------------------
    # 4. Time-based anomalies (user-relative)
    # ----------------------------
    user_hour_stats = (
        df.groupby("user_id")["hour"]
        .median()
        .reset_index()
        .rename(columns={"hour": "user_median_hour"})
    )

    df = df.merge(user_hour_stats, on="user_id", how="left")

    df["hour_deviation"] = (df["hour"] - df["user_median_hour"]).abs()
    df["is_unusual_hour"] = (df["hour_deviation"] > 6).astype(int)

    # ----------------------------
    # 5. Transaction type rarity
    # ----------------------------
    txn_type_counts = (
        df.groupby(["user_id", "transaction_type"])
        .size()
        .reset_index(name="txn_type_count")
    )

    df = df.merge(
        txn_type_counts,
        on=["user_id", "transaction_type"],
        how="left"
    )

    df["is_rare_txn_type"] = (df["txn_type_count"] < 5).astype(int)

    # ----------------------------
    # 6. New device detection
    # ----------------------------
    df["device_seen_before"] = (
        df.groupby("user_id")["device_id"]
        .transform(lambda x: x.duplicated().astype(int))
    )

    df["new_device"] = (df["device_seen_before"] == 0).astype(int)

    # ----------------------------
    # 7. New location detection
    # ----------------------------
    df["location_seen_before"] = (
        df.groupby("user_id")["location"]
        .transform(lambda x: x.duplicated().astype(int))
    )

    df["new_location"] = (df["location_seen_before"] == 0).astype(int)

    # ----------------------------
    # Cleanup (optional but neat)
    # ----------------------------
    df.drop(
        columns=[
            "device_seen_before",
            "location_seen_before"
        ],
        inplace=True
    )

    return df