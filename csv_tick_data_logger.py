import os
import sys
import time
import threading
import signal
import pandas as pd
from binance import ThreadedWebsocketManager
from bot_variables import api_key, secret_key


class TickCSVLogger:
    def __init__(self, symbol="BTCUSDT", csv_filename=None):
        self.symbol = symbol
        self.csv_filename = csv_filename or f"{symbol}_ticks.csv"
        self.df = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume", "Complete", "Timestamp"])
        self.twm = None
        self.is_running = False

        # CSV initialisieren
        try:
            if os.path.exists(self.csv_filename):
                os.chmod(self.csv_filename, 0o666)
                os.remove(self.csv_filename)
            self.df.to_csv(self.csv_filename, index=False)
            print(f"✓ Neue Tick-CSV erstellt: {self.csv_filename}")
        except Exception as e:
            print(f"Fehler beim Erstellen der CSV: {e}")

    def stream_ticks(self, msg):
        """Verarbeitet WebSocket Nachrichten und speichert jede Zeile als Tick"""
        if not self.is_running:
            return
        try:
            k = msg["k"]
            if k["x"]:  # nur fertige Candles speichern, wenn du möchtest, sonst alles
                row = {
                    "Open": float(k["o"]),
                    "High": float(k["h"]),
                    "Low": float(k["l"]),
                    "Close": float(k["c"]),
                    "Volume": float(k["v"]),
                    "Complete": k["x"],
                    "Timestamp": pd.to_datetime(k["t"], unit="ms")
                }
                pd.DataFrame([row]).to_csv(self.csv_filename, mode='a', header=False, index=False)
        except Exception as e:
            if self.is_running:
                print(f"Fehler beim Verarbeiten eines Ticks: {e}")

    def start_logging(self, api_key, api_secret, duration_minutes=None):
        if self.is_running:
            print("Logger läuft bereits!")
            return
        self.twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
        self.twm.start()
        self.twm.start_kline_socket(callback=self.stream_ticks, symbol=self.symbol, interval="1s")
        self.is_running = True

        # optional: Stop nach Duration
        if duration_minutes:
            def stop_after():
                time.sleep(duration_minutes*60)
                self.stop_logging()
            threading.Thread(target=stop_after, daemon=True).start()

        print("Tick-Logging gestartet. Ctrl+C zum Stoppen.")

        def signal_handler(sig, frame):
            self.stop_logging()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

        while self.is_running:
            time.sleep(1)

    def stop_logging(self):
        if self.twm and self.is_running:
            self.is_running = False
            try:
                self.twm.stop()
                time.sleep(1)
                print(f"Logging gestoppt. CSV gespeichert: {self.csv_filename}")
            except Exception as e:
                print(f"Fehler beim Stoppen: {e}")

# Beispiel:
if __name__ == "__main__":
    try:
        from bot_variables import api_key, secret_key
    except ImportError:
        print("API Keys nicht gefunden!")
        sys.exit(1)

    logger = TickCSVLogger()
    logger.start_logging(api_key=api_key, api_secret=secret_key)