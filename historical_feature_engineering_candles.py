#!/usr/bin/env python3
"""
Feature Engineering Präzise Candle-Version
Berechnet alle technischen Indikatoren korrekt, entfernt Leakage
und behält nur die Zeilen, bei denen alle Rolling/EMA/Fensterwerte vollständig berechnet sind.
"""

import pandas as pd
import numpy as np

INPUT_CSV = "historical.csv"
OUTPUT_CSV = "historical_features.csv"

def load_data():
    df = pd.read_csv(INPUT_CSV, parse_dates=['Timestamp'])
    df = df.sort_values('Timestamp').reset_index(drop=True)
    return df

def compute_rsi(series, window):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_technical_indicators(df):
    # Basis-Kennzahlen
    df['hl_range'] = df['High'] - df['Low']
    df['oc_change'] = df['Close'] - df['Open']
    df['returns'] = df['Close'].pct_change()

    # Gleitende Durchschnitte
    for window in [5, 10, 20, 50, 100]:
        df[f'sma_{window}'] = df['Close'].rolling(window=window).mean()
        df[f'ema_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()

    # Volatilität & Momentum
    for window in [5, 10, 20]:
        df[f'vol_{window}'] = df['Close'].rolling(window=window).std()
        df[f'rsi_{window}'] = compute_rsi(df['Close'], window)
        df[f'vol_mean_{window}'] = df['Volume'].rolling(window=window).mean()
        df[f'vol_std_{window}'] = df['Volume'].rolling(window=window).std()

    # Bollinger Bands
    window = 20
    sma = df['Close'].rolling(window=window).mean()
    std = df['Close'].rolling(window=window).std()
    df[f'bb_upper_{window}'] = sma + 2*std
    df[f'bb_lower_{window}'] = sma - 2*std

    # Lag-Features (nur hier shift, damit kein Leakage entsteht)
    lag_columns = ['Close', 'Volume', 'returns']
    max_lag = 5
    for col in lag_columns:
        for lag in range(1, max_lag + 1):
            df[f"{col}_lag_{lag}"] = df[col].shift(lag)

    # WICHTIG: Alle Zeilen entfernen, bei denen irgendein Wert aufgrund des Rolling/Fensters noch NaN ist
    df = df.dropna().reset_index(drop=True)

    return df

def save_features(df):
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✓ Präzise Features gespeichert in {OUTPUT_CSV} ({len(df)} Zeilen)")

def run_feature_engineering():
    df = load_data()
    df = add_technical_indicators(df)
    save_features(df)

if __name__ == "__main__":
    run_feature_engineering()