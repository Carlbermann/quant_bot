#!/usr/bin/env python3
"""
Feature Engineering Module
Liest die CSV mit Marktdaten ein und berechnet relevante Kennzahlen
für Quant-Crypto-Preisprognosen. Erstellt eine neue CSV mit allen Features.
"""

import pandas as pd
import numpy as np
from pathlib import Path

INPUT_CSV = "BTCUSDT_1m_data.csv"
OUTPUT_CSV = "BTCUSDT_1m_features.csv"
df = pd.read_csv(INPUT_CSV)


def load_data():
    """Liest die Original-CSV ein"""
    df = pd.read_csv(INPUT_CSV, parse_dates=['Timestamp'])
    df = df.sort_values('Timestamp').reset_index(drop=True)
    return df

def add_technical_indicators(df):
    """Berechnet technische Kennzahlen und fügt sie als Spalten hinzu"""
    
    # 1. Preisbasierte Kennzahlen
    df['hl_range'] = df['High'] - df['Low']
    df['oc_change'] = df['Close'] - df['Open']
    df['returns'] = df['Close'].pct_change()
    
    # 2. Gleitende Durchschnitte
    for window in [5, 10, 20, 50, 100]:
        df[f'sma_{window}'] = df['Close'].rolling(window).mean()
        df[f'ema_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()
    
    # 3. Volatilitätskennzahlen
    for window in [5, 10, 20]:
        df[f'vol_{window}'] = df['Close'].rolling(window).std()
    
    # 4. Momentum-Indikatoren
    for window in [5, 10, 20]:
        df[f'rsi_{window}'] = compute_rsi(df['Close'], window)
    
    # 5. Bollinger Bands
    for window in [20]:
        sma = df['Close'].rolling(window).mean()
        std = df['Close'].rolling(window).std()
        df[f'bb_upper_{window}'] = sma + (2 * std)
        df[f'bb_lower_{window}'] = sma - (2 * std)
    
    # 6. Volumen-Indikatoren
    for window in [5, 10, 20]:
        df[f'vol_mean_{window}'] = df['Volume'].rolling(window).mean()
        df[f'vol_std_{window}'] = df['Volume'].rolling(window).std()
    
    # Optional: Drop NaN-Zeilen, die durch Rolling entstehen
    df = df.dropna().reset_index(drop=True)
    
    return df

def compute_rsi(series, window):
    """Berechnet den RSI (Relative Strength Index)"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def save_features(df):
    """Speichert die erweiterte CSV"""
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✓ Features gespeichert in {OUTPUT_CSV}")

def run_feature_engineering():
    """Kompletter Workflow"""
    df = load_data()
    df = add_technical_indicators(df)
    save_features(df)

if __name__ == "__main__":
    run_feature_engineering()