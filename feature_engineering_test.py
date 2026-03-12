#!/usr/bin/env python3
"""
Feature Engineering Module (unpräzise Candle-Daten, leakage-frei)
"""

import pandas as pd
import numpy as np

INPUT_CSV = "BTCUSDT_1m_data.csv"
OUTPUT_CSV = "BTCUSDT_1m_features.csv"

def load_data():
    df = pd.read_csv(INPUT_CSV, parse_dates=['Timestamp'])
    df = df.sort_values('Timestamp').reset_index(drop=True)
    return df

def compute_rsi(series, window, min_periods=1):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window, min_periods=min_periods).mean()
    avg_loss = loss.rolling(window, min_periods=min_periods).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_technical_indicators(df):
    df['hl_range'] = (df['High'] - df['Low']).shift(1)
    df['oc_change'] = (df['Close'] - df['Open']).shift(1)
    df['returns'] = df['Close'].pct_change().shift(1)

    for window in [5, 10, 20, 50, 100]:
        df[f'sma_{window}'] = df['Close'].rolling(window, min_periods=1).mean().shift(1)
        df[f'ema_{window}'] = df['Close'].ewm(span=window, adjust=False).mean().shift(1)

    for window in [5, 10, 20]:
        df[f'vol_{window}'] = df['Close'].rolling(window, min_periods=1).std().shift(1)
        df[f'rsi_{window}'] = compute_rsi(df['Close'], window, min_periods=1).shift(1)
        df[f'vol_mean_{window}'] = df['Volume'].rolling(window, min_periods=1).mean().shift(1)
        df[f'vol_std_{window}'] = df['Volume'].rolling(window, min_periods=1).std().shift(1)

    # Bollinger Bands
    window = 20
    sma = df['Close'].rolling(window, min_periods=1).mean()
    std = df['Close'].rolling(window, min_periods=1).std()
    df[f'bb_upper_{window}'] = (sma + 2*std).shift(1)
    df[f'bb_lower_{window}'] = (sma - 2*std).shift(1)

    # Lag-Features
    for lag in range(1, 6):
        df[f'Close_lag_{lag}'] = df['Close'].shift(lag)
        df[f'Volume_lag_{lag}'] = df['Volume'].shift(lag)
        df[f'returns_lag_{lag}'] = df['returns'].shift(lag)

    df = df.dropna().reset_index(drop=True)
    return df

def save_features(df):
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✓ Features gespeichert in {OUTPUT_CSV}")

def run_feature_engineering():
    df = load_data()
    df = add_technical_indicators(df)
    save_features(df)

if __name__ == "__main__":
    run_feature_engineering()