# historical_candles_robust.py
import csv
from datetime import datetime, timedelta, timezone
from binance.client import Client
from bot_variables import api_key, secret_key

def fetch_historical_candles(symbol='BTCUSDT', days=30, interval='1m', filename='historical.csv'):
    client = Client(api_key, secret_key)
    start_dt = datetime.now(timezone.utc) - timedelta(days=days)
    end_dt = datetime.now(timezone.utc)

    all_klines = []
    while start_dt < end_dt:
        # Binance erlaubt max. 1000 Kerzen pro Anfrage
        klines = client.get_historical_klines(
            symbol, interval,
            start_str=start_dt.strftime("%d %b %Y %H:%M:%S"),
            limit=1000
        )
        if not klines:
            break
        all_klines.extend(klines)
        # Timestamp der letzten Kerze + 1ms als Start für nächste Abfrage
        start_dt = datetime.fromtimestamp(klines[-1][0]/1000, tz=timezone.utc) + timedelta(milliseconds=1)

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Open','High','Low','Close','Volume','Complete','Timestamp'])
        for k in all_klines:
            ts = datetime.fromtimestamp(k[0]/1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([k[1], k[2], k[3], k[4], k[5], True, ts])

if __name__ == "__main__":
    fetch_historical_candles(days=30)