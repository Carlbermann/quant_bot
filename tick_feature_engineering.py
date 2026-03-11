#!/usr/bin/env python3
"""
Feature Engineering für Tick-Daten
Liest die Tick-CSV ein, berechnet Features inklusive Lag-Features, speichert als neue CSV.
"""

import pandas as pd
import numpy as np

INPUT_CSV = "BTCUSDT_ticks.csv"
OUTPUT_CSV = "BTCUSDT_ticks_features.csv"


def load_data():
    """Lädt die Tick-CSV und sortiert nach Timestamp"""
    df = pd.read_csv(INPUT_CSV, parse_dates=['Timestamp'])
    df = df.sort_values('Timestamp').reset_index(drop=True)
    return df


def compute_rsi(series, window, min_periods=1):
    """Berechnet den RSI (Relative Strength Index)"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window, min_periods=min_periods).mean()
    avg_loss = loss.rolling(window, min_periods=min_periods).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def add_lag_features(df, columns, max_lag=5):
    """
    Erstellt Lag-Features für angegebene Spalten

    Args:
        df: DataFrame
        columns: Liste der Spaltennamen, für die Lags erstellt werden
        max_lag: maximale Lag-Anzahl
    """
    for col in columns:
        for lag in range(1, max_lag + 1):
            df[f"{col}_lag_{lag}"] = df[col].shift(lag)
    return df


def add_technical_indicators(df):
    """Berechnet technische Kennzahlen und fügt sie als Spalten hinzu"""
    
    # 1. Preisbasierte Kennzahlen
    df['hl_range'] = df['High'] - df['Low']
    df['oc_change'] = df['Close'] - df['Open']
    df['returns'] = df['Close'].pct_change()

    # 2. Gleitende Durchschnitte
    for window in [5, 10, 20, 50, 100]:
        df[f'sma_{window}'] = df['Close'].rolling(window, min_periods=1).mean()
        df[f'ema_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()

    # 3. Volatilitätskennzahlen & Momentum
    for window in [5, 10, 20]:
        df[f'vol_{window}'] = df['Close'].rolling(window, min_periods=1).std()
        df[f'rsi_{window}'] = compute_rsi(df['Close'], window, min_periods=1)
        df[f'vol_mean_{window}'] = df['Volume'].rolling(window, min_periods=1).mean()
        df[f'vol_std_{window}'] = df['Volume'].rolling(window, min_periods=1).std()

    # 4. Bollinger Bands
    window = 20
    sma = df['Close'].rolling(window, min_periods=1).mean()
    std = df['Close'].rolling(window, min_periods=1).std()
    df[f'bb_upper_{window}'] = sma + 2*std
    df[f'bb_lower_{window}'] = sma - 2*std

    # 5. Lag-Features
    lag_columns = ['Close', 'Volume', 'returns']
    df = add_lag_features(df, lag_columns, max_lag=5)

    # Optional: NaNs, die durch Rolling und Lag entstehen, entfernen
    df = df.dropna().reset_index(drop=True)

    return df


def save_features(df):
    """Speichert die erweiterten Features als CSV"""
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✓ Tick-Features gespeichert in {OUTPUT_CSV}")


def run_feature_engineering():
    """Kompletter Workflow"""
    df = load_data()
    df = add_technical_indicators(df)
    save_features(df)


if __name__ == "__main__":
    run_feature_engineering()