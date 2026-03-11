# quant_bot
A Python project that connects to the Binance API, collects BTCUSDT market data, and allows testing of signal-based trading strategies using historical and live data.



## **Setup**

1. **API-Zugang erstellen:**  
   Erstelle ein Python-Modul `bot_variables.py` im gleichen Verzeichnis wie die Skripte und definiere dort:  

```python
# bot_variables.py
api_key = "DEIN_API_KEY_HIER"
api_secret = "DEIN_API_SECRET_HIER"



# Feature Engineering für Quant-Crypto-Trading

Dieses Repository enthält Skripte zur Erstellung von Feature-Matrizen für den Quant-Handel mit BTC/USDT.  
Es werden drei verschiedene Feature-Matrizen unterstützt:



1. **Tick-Features** tick_feature_engineering.py 
Basis:(`BTCUSDT_ticks_features.csv`):  
   Hochfrequente Features auf Tick-Basis (1s), inkl. Lag-Features für Close, Volume und Returns.  
   Ideal für Modelle, die auf sehr kurzfristige Preisbewegungen reagieren.

2. **Candle-Features – präzise** feature_engineering.py 
Basis: (`BTCUSDT_1m_features.csv`):  
   Features auf Minutenkerzenbasis, sehr präzise Berechnungen für Gleitende Durchschnitte, Volatilität, RSI und Bollinger Bands.  
   Lag-Features sind pro Feature gruppiert (`Close_lag_1,Volume_lag_1,returns_lag_1,...`), optimal für sequenzielle ML-Modelle. 
   Es werden mind. 100 candles benötigt für präzise Berechnungen.  

3. **Candle-Features – weniger präzise** feature_engineering_test.py 
Basis: (`BTCUSDT_1m_features.csv`):  
   Features auf Minutenkerzenbasis, Keine Mindestanzahl an Datenpunkten benötigt, dafür etwas unpräzisere Werte.  
   Lag-Features sind wie bei Tick-Features einfach hintereinander (`Close_lag_1 … Close_lag_5`, `Volume_lag_1 … Volume_lag_5`, `returns_lag_1 … returns_lag_5`).  

---

