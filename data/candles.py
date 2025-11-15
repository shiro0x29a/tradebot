import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def fetch_ohlcv(exchange, symbol, timeframe, start, end):
    start_dt = pd.to_datetime(start).tz_localize('UTC')
    end_dt = pd.to_datetime(end).tz_localize('UTC')
    
    since = int(start_dt.timestamp() * 1000)
    until = int(end_dt.timestamp() * 1000)
    
    ohlcv = []
    current_since = since
    
    while current_since < until:
        try:
            data = exchange.fetch_ohlcv(symbol, timeframe, current_since, limit=1000)
            if not data:
                break
            ohlcv += data
            current_since = data[-1][0] + 1
            time.sleep(0.1)
        except Exception as e:
            print(f"Ошибка: {e}, повтор через 5 сек...")
            time.sleep(5)
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
    df.set_index('timestamp', inplace=True)
    return df.loc[start_dt:end_dt]
