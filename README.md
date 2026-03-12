# quant_bot
A Python project that connects to the Binance API, collects BTCUSDT market data, and allows testing of signal-based trading strategies using historical and live data.

Setup

API-Zugang erstellen
Der Bot verwendet die Binance API. für die Einrichtung gucken unter:
Binance API Documentation


Erstelle ein Python-Modul bot_variables.py im gleichen Verzeichnis wie die Skripte und definiere dort:

# bot_variables.py
api_key = "DEIN_API_KEY_HIER"
api_secret = "DEIN_API_SECRET_HIER"

Python-Abhängigkeiten installieren

pip install -r requirements.txt
Feature Engineering für Quant-Crypto-Trading




Dieses Repository enthält Skripte zur Erstellung von Feature-Matrizen für den Quant-Handel mit BTC/USDT.
Es werden drei verschiedene Feature-Matrizen unterstützt:

1. Tick-Features – Hochfrequent

Script: tick_feature_engineering.py
Output: BTCUSDT_ticks_features.csv
Hochfrequente Tick-Daten (1s)
Lag-Features für Close, Volume und Returns
Ideal für Modelle, die auf sehr kurzfristige Preisbewegungen reagieren
Alle Zeilen werden genutzt, keine Mindestanzahl für Rolling-Fenster

2. Candle-Features – präzise

Script: feature_engineering.py
Output: BTCUSDT_1m_features.csv
Features auf Minutenkerzenbasis
Sehr präzise Berechnungen für SMA, EMA, Volatilität, RSI und Bollinger Bands
Lag-Features gruppiert: Close_lag_1, Volume_lag_1, returns_lag_1, ...
Mindestanzahl an Candles erforderlich (z. B. 100 für Rolling100) → die ersten 100 Zeilen werden entfernt
Optimal für sequenzielle ML-Modelle
Leakage-frei: Lag-Features korrekt shift(1)

3. Candle-Features – Test/unkritisch

Script: feature_engineering_test.py
Output: BTCUSDT_1m_features.csv
Features auf Minutenkerzenbasis, schneller berechnet
Keine Mindestanzahl an Datenpunkten erforderlich
Etwas unpräzisere Werte
Lag-Features wie bei Tick-Features, einfach hintereinander
Alle Zeilen werden genutzt

ML-Module

Alle ML-Module arbeiten auf Basis der erzeugten Feature-CSVs:

Modul	Funktion
ml_dataset_builder.py	Lädt Features, erstellt Labels, baut Trainingsdaten, speichert ml_model.pkl
ml_backtest.py	Führt Backtests des Modells auf historischen Daten durch
walk_forward_backtest.py	Walk-Forward Backtesting, um Robustheit zu testen
ml_live_signal.py	Lädt ml_model.pkl und berechnet Live-Signale
feature_importance.py	Analysiert das trainierte Modell, zeigt die wichtigsten Features an
Output / Ergebnisse

Nach Ausführung der Feature-Engineering-Skripte und des Trainings:

Feature CSVs:

BTCUSDT_1m_features.csv – präzise Candle-Features, weniger Zeilen

BTCUSDT_1m_features.csv – Test-Candle-Features, alle Zeilen

BTCUSDT_ticks_features.csv – Tick-Features, alle Zeilen

ML-Model:

ml_model.pkl – gespeichertes trainiertes Modell

Hinweise

Präzision vs. Geschwindigkeit:

Für reale ML-Trainings und Backtests immer die präzise CSV verwenden

Für schnelle Tests oder Experimente kann die Test CSV genutzt werden

Leakage-frei:

Alle Lag-Features (shift(1)) korrekt implementiert

Rolling-Berechnungen nur auf Vergangenheitsdaten

