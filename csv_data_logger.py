import signal
import sys
import threading
import time
from binance import ThreadedWebsocketManager
import pandas as pd
import os
from datetime import datetime
import numpy as np


class CSVDataLogger:
    def __init__(self, symbol="BTCUSDT", interval="1m", csv_filename=None):
        """
        Initialize the CSV Data Logger
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            interval: Timeframe (e.g., "1m", "5m", "1h", "1d")
            csv_filename: Custom CSV filename (auto-generated if not provided)
        """
        self.symbol = symbol
        self.interval = interval
        self.csv_filename = csv_filename or f"{symbol}_{interval}_data.csv"
        self.df = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume", "Complete", "Timestamp"])
        self.twm = None
        self.is_running = False
        
        # Always create fresh CSV file (replace existing)
        try:
            # Force delete existing file even if read-only
            if os.path.exists(self.csv_filename):
                try:
                    os.chmod(self.csv_filename, 0o666)  # Make writable
                    os.remove(self.csv_filename)  # Delete old file
                except:
                    pass  # Ignore errors, continue to create new
            
            self.df.to_csv(self.csv_filename, index=False)
            print(f"Created new CSV file: {self.csv_filename}")
        except Exception as e:
            print(f"Error creating CSV file: {e}")
            return
    
    def stream_candles(self, msg):

        if not self.is_running:
            return

        try:
            kline = msg["k"]

            # Check if candle is finished
            if not kline["x"]:
                return

            start_time = pd.to_datetime(kline["t"], unit="ms")

            new_row = {
                "Open": float(kline["o"]),
                "High": float(kline["h"]),
                "Low": float(kline["l"]),
                "Close": float(kline["c"]),
                "Volume": float(kline["v"]),
                "Complete": True,
                "Timestamp": start_time
            }

            new_df = pd.DataFrame([new_row])

            new_df.to_csv(
                self.csv_filename,
                mode="a",
                header=False,
                index=False
            )

            print(f"Candle saved: {start_time}")

        except Exception as e:
            if self.is_running:
                print(f"Error processing message: {e}")
    
    def start_logging(self, api_key="your_api_key", api_secret="your_api_secret", duration_minutes=None):
        """
        Start logging data to CSV
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            duration_minutes: Stop logging after X minutes (None for infinite)
        """
        if self.is_running:
            print("Logger is already running!")
            return
            
        print(f"Starting CSV logging for {self.symbol} {self.interval}...")
        print(f"Data will be saved to: {self.csv_filename}")
        
        # Initialize the WebSocket Manager
        self.twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret, tld="com")
        self.twm.start()
        
        # Start the WebSocket for the specified symbol and interval
        self.twm.start_kline_socket(callback=self.stream_candles, symbol=self.symbol, interval=self.interval)
        
        self.is_running = True
        
        if duration_minutes:
            print(f"Logging will stop automatically after {duration_minutes} minutes")
            # Schedule stop using threading
            def stop_after_duration():
                time.sleep(duration_minutes * 60)
                if self.is_running:
                    print(f"\nStopping logging after {duration_minutes} minutes...")
                    self.stop_logging()
            stop_thread = threading.Thread(target=stop_after_duration, daemon=True)
            stop_thread.start()
        
        print("WebSocket logging started. Press Ctrl+C to stop.")
        
        # Set up signal handler for Ctrl+C
        def signal_handler(sig, frame):
            print("\nStopping logging...")
            self.stop_logging()
            print("Program terminated.")
            sys.exit(0)  # Force exit the entire program
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            # Keep the main thread alive
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping logging...")
            self.stop_logging()
    
    def stop_logging(self):
        """Stop the WebSocket logging"""
        if self.twm and self.is_running:
            try:
                self.is_running = False  # Set flag first
                
                # More aggressive WebSocket termination
                try:
                    self.twm.stop()
                except:
                    pass
                
                # Wait a bit for graceful shutdown
                time.sleep(1)
                
                # Force kill all WebSocket threads
                if hasattr(self.twm, '_threads'):
                    for thread_name, thread in self.twm._threads.items():
                        if thread.is_alive():
                            try:
                                # Force stop the thread
                                thread._stop()
                            except:
                                pass
                
                # Additional force stop
                if hasattr(self.twm, 'running'):
                    self.twm.running = False
                
                print(f"Logging stopped. Data saved to {self.csv_filename}")
                
                # Show CSV file info
                if os.path.exists(self.csv_filename):
                    df = pd.read_csv(self.csv_filename)
                    print(f"CSV contains {len(df)} records")
                    
                    # Lock the CSV file by making it read-only (optional)
                    try:
                        os.chmod(self.csv_filename, 0o444)  # Read-only
                        print(f"CSV file locked (read-only) to prevent further changes")
                    except:
                        pass
                else:
                    print("Warning: CSV file not found")
                    
            except Exception as e:
                print(f"Error stopping logging: {e}")
                # Force stop even if there's an error
                self.is_running = False
                
                # Try to force stop the WebSocket manager
                try:
                    if self.twm:
                        self.twm.running = False
                except:
                    pass
    
    def get_saved_data(self, rows=None):
        """
        Read and return data from the CSV file
        
        Args:
            rows: Number of recent rows to return (None for all)
        """
        if os.path.exists(self.csv_filename):
            df = pd.read_csv(self.csv_filename)
            if rows:
                return df.tail(rows)
            return df
        else:
            print(f"No data file found: {self.csv_filename}")
            return pd.DataFrame()


# Example usage functions
def log_btc_data(interval="1m", duration_minutes=None):
    """Quick function to start logging BTCUSDT data"""
    logger = CSVDataLogger(symbol="BTCUSDT", interval=interval)
    logger.start_logging(duration_minutes=duration_minutes)

def log_custom_symbol(symbol, interval="1m", duration_minutes=None):
    """Quick function to start logging custom symbol data"""
    logger = CSVDataLogger(symbol=symbol, interval=interval)
    logger.start_logging(duration_minutes=duration_minutes)

if __name__ == "__main__":
    # Auto-start logging when module is run directly
    # Import your API keys
    try:
        from bot_variables import api_key, secret_key
    except ImportError:
        print("Error: Could not import api_key and secret_key from bot_variables.py")
        print("Please make sure bot_variables.py exists with your Binance API credentials")
        exit()
    
    print("Starting automatic CSV data logging...")
    print("Press Ctrl+C to stop")
    
    # Create logger and start automatically
    logger = CSVDataLogger(symbol="BTCUSDT", interval="1m")
    logger.start_logging(api_key=api_key, api_secret=secret_key)
