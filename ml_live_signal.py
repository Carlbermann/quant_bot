import pandas as pd
import joblib


MODEL_FILE = "ml_model.pkl"
FEATURE_FILE = "BTCUSDT_1m_features.csv"


def load_model():

    return joblib.load(MODEL_FILE)


def load_latest_features():

    df = pd.read_csv(FEATURE_FILE)

    return df.iloc[-1:]


def generate_signal(model, features):

    drop_cols = ["Timestamp","Complete"]

    X = features.drop(columns=drop_cols, errors="ignore")

    signal = model.predict(X)[0]

    return signal


def main():

    model = load_model()

    features = load_latest_features()

    signal = generate_signal(model, features)

    if signal == 1:
        print("LONG SIGNAL")

    elif signal == -1:
        print("SHORT SIGNAL")

    else:
        print("NO TRADE")


if __name__ == "__main__":
    main()