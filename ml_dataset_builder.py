import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# ==============================
# CONFIG
# ==============================

FEATURE_FILE = "BTCUSDT_1m_features.csv"
FUTURE_STEPS = 5
RETURN_THRESHOLD = 0.001


# ==============================
# LOAD DATA
# ==============================

def load_features():

    df = pd.read_csv(FEATURE_FILE)

    return df


# ==============================
# CREATE LABELS
# ==============================

def create_labels(df):

    df["future_close"] = df["Close"].shift(-FUTURE_STEPS)

    df["future_return"] = (
        df["future_close"] - df["Close"]
    ) / df["Close"]

    df["y"] = 0

    df.loc[df["future_return"] > RETURN_THRESHOLD, "y"] = 1
    df.loc[df["future_return"] < -RETURN_THRESHOLD, "y"] = -1

    return df


# ==============================
# BUILD DATASET
# ==============================

def build_dataset(df):

    df = df.dropna()

    drop_cols = [
        "Timestamp",
        "future_close",
        "future_return",
        "y",
        "Complete"
    ]

    X = df.drop(columns=drop_cols, errors="ignore")

    y = df["y"]

    return X, y


# ==============================
# TRAIN MODEL
# ==============================

def train_model(X, y):

    split = int(len(X) * 0.8)

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    return model


# ==============================
# MAIN
# ==============================

def main():

    print("Loading features...")

    df = load_features()

    print("Creating labels...")

    df = create_labels(df)

    print("Building dataset...")

    X, y = build_dataset(df)

    print("Training model...")

    model = train_model(X, y)

    print("Saving model...")

    import joblib
    joblib.dump(model, "ml_model.pkl")

    print("Model saved.")

if __name__ == "__main__":
    main()
