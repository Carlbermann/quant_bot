import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier


FEATURE_FILE = "BTCUSDT_1m_features.csv"

TRAIN_WINDOW = 5000
TEST_WINDOW = 1000

FUTURE_STEPS = 5
RETURN_THRESHOLD = 0.0005

INITIAL_CAPITAL = 10000
TRADE_SIZE = 0.1


def create_labels(df):

    df["future_close"] = df["Close"].shift(-FUTURE_STEPS)

    df["future_return"] = (
        df["future_close"] - df["Close"]
    ) / df["Close"]

    df["y"] = 0

    df.loc[df["future_return"] > RETURN_THRESHOLD, "y"] = 1
    df.loc[df["future_return"] < -RETURN_THRESHOLD, "y"] = -1

    return df


def build_features(df):

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


def run_backtest(predictions, prices, capital):

    equity_curve = []

    for i in range(len(predictions)-FUTURE_STEPS):

        signal = predictions[i]

        entry = prices[i]
        exit = prices[i+FUTURE_STEPS]

        position = capital * TRADE_SIZE

        pnl = 0

        if signal == 1:
            pnl = position * ((exit-entry)/entry)

        elif signal == -1:
            pnl = position * ((entry-exit)/entry)

        capital += pnl

        equity_curve.append(capital)

    return capital, equity_curve


def main():

    df = pd.read_csv(FEATURE_FILE)

    df = create_labels(df)

    df = df.dropna()

    X, y = build_features(df)

    prices = df["Close"].values

    capital = INITIAL_CAPITAL

    equity_curve = []

    start = TRAIN_WINDOW

    while start + TEST_WINDOW < len(df):

        train_start = start - TRAIN_WINDOW
        train_end = start

        test_end = start + TEST_WINDOW

        X_train = X.iloc[train_start:train_end]
        y_train = y.iloc[train_start:train_end]

        X_test = X.iloc[start:test_end]

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=8
        )

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        test_prices = prices[start:test_end]

        capital, curve = run_backtest(
            predictions,
            test_prices,
            capital
        )

        equity_curve += curve

        start += TEST_WINDOW

    print("Final Capital:", round(capital,2))


if __name__ == "__main__":
    main()