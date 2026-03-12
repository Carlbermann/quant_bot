import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


# ==============================
# CONFIG
# ==============================

FEATURE_FILE = "BTCUSDT_1m_features.csv"

FUTURE_STEPS = 5
RETURN_THRESHOLD = 0.0005

INITIAL_CAPITAL = 10000
TRADE_SIZE = 0.1


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

    return X, y, df


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

    return model, predictions, split


# ==============================
# BACKTEST
# ==============================

def run_backtest(df, predictions, split):

    capital = INITIAL_CAPITAL

    equity_curve = []

    prices = df["Close"].iloc[split:].values

    for i in range(len(predictions)-FUTURE_STEPS):

        signal = predictions[i]

        entry_price = prices[i]
        exit_price = prices[i + FUTURE_STEPS]

        position_size = capital * TRADE_SIZE

        pnl = 0

        if signal == 1:

            pnl = position_size * (
                (exit_price - entry_price) / entry_price
            )

        elif signal == -1:

            pnl = position_size * (
                (entry_price - exit_price) / entry_price
            )

        capital += pnl

        equity_curve.append(capital)

    return capital, equity_curve


# ==============================
# PERFORMANCE METRICS
# ==============================

def performance_metrics(equity_curve):

    returns = np.diff(equity_curve) / equity_curve[:-1]

    total_return = (
        equity_curve[-1] / equity_curve[0] - 1
    )

    sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0

    max_drawdown = np.min(
        equity_curve / np.maximum.accumulate(equity_curve) - 1
    )

    print("\nPerformance Results\n")

    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2%}")


# ==============================
# MAIN
# ==============================

def main():

    print("Loading features...")

    df = load_features()

    print("Creating labels...")

    df = create_labels(df)

    print("Building dataset...")

    X, y, df = build_dataset(df)

    print("Training model...")

    model, predictions, split = train_model(X, y)

    print("Running backtest...")

    final_capital, equity_curve = run_backtest(
        df,
        predictions,
        split
    )

    print("\nFinal Capital:", round(final_capital, 2))

    performance_metrics(equity_curve)


if __name__ == "__main__":
    main()