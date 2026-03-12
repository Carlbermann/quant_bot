import pandas as pd
from sklearn.ensemble import RandomForestClassifier


FEATURE_FILE = "BTCUSDT_1m_features.csv"


def main():

    df = pd.read_csv(FEATURE_FILE)

    df = df.dropna()

    drop_cols = ["Timestamp","Complete"]

    X = df.drop(columns=drop_cols, errors="ignore")

    y = (df["Close"].shift(-5) > df["Close"]).astype(int)

    X = X.iloc[:-5]
    y = y.iloc[:-5]

    model = RandomForestClassifier(n_estimators=200)

    model.fit(X,y)

    importances = model.feature_importances_

    features = X.columns

    importance_df = pd.DataFrame({
        "feature":features,
        "importance":importances
    })

    importance_df = importance_df.sort_values(
        "importance",
        ascending=False
    )

    print("\nTop Features\n")

    print(importance_df.head(20))


if __name__ == "__main__":
    main()