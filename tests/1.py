import ccxt
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

SYMBOL = "ETHUSDT"
INITIAL_BALANCE = 10000
COMMISSION = 0.001

LIMIT = 2500
VOLUME_LOOKBACK = 60
VOLUME_MULTIPLIER = 2.0

def fetch_klines(symbol='ETHUSDT', interval='1d', total_bars=2500):
    """Загрузка данных с 2020 года"""
    exchange = ccxt.binance()
    data = []
    
    # Начинаем с 2020 года
    since = exchange.parse8601('2020-01-01T00:00:00Z')
    
    while len(data) < total_bars:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, interval, since=since, limit=1000)
            if not ohlcv:
                break
                
            data.extend(ohlcv)
            since = ohlcv[-1][0] + exchange.parse_timeframe(interval) * 1000
            time.sleep(0.1)
            
        except Exception as e:
            print(f"CCXT Error: {e}")
            break

    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df = df.drop_duplicates('timestamp')
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Обрезаем до нужного количества баров
    if len(df) > total_bars:
        df = df.tail(total_bars)
    
    return df

def backtest(df):
    """Твоя объемная стратегия"""
    results = []
    for i in range(VOLUME_LOOKBACK, len(df) - 1):
        prev_60 = df.iloc[i - VOLUME_LOOKBACK:i]
        cur = df.iloc[i]
        next_bar = df.iloc[i + 1]

        avg_vol = prev_60["volume"].mean()
        is_red = cur["close"] < cur["open"]
        vol_ok = cur["volume"] >= VOLUME_MULTIPLIER * avg_vol

        if is_red and vol_ok:
            entry = next_bar["open"]
            exit_ = next_bar["close"]
            ret = (exit_ - entry) / entry * 100.0
            results.append({
                "signal_time": cur["timestamp"],
                "entry": entry,
                "exit": exit_,
                "ret_%": ret,
            })
    return pd.DataFrame(results)

def main():
    print("Загрузка данных с 2020 года...")
    df = fetch_klines(SYMBOL, "1d", 2500)
    bt = backtest(df)

    if bt.empty:
        print("Сигналов не найдено.")
        return

    print(f"\n=== РЕЗУЛЬТАТЫ ===")
    print(f"Период: {df['timestamp'].iloc[0].date()} - {df['timestamp'].iloc[-1].date()}")
    print(f"Сделок: {len(bt)}")
    
    wins = (bt["ret_%"] > 0).sum()
    losses = (bt["ret_%"] <= 0).sum()
    total_return = bt["ret_%"].sum()
    win_rate = (wins / len(bt)) * 100
    
    print(f"Побед: {wins} ({win_rate:.1f}%)")
    print(f"Поражений: {losses}")
    print(f"Общая доходность: {total_return:.2f}%")
    
    # Расчет баланса
    final_balance = INITIAL_BALANCE
    for ret in bt["ret_%"]:
        final_balance *= (1 + ret/100) * (1 - COMMISSION)
    
    print(f"Начальный баланс: ${INITIAL_BALANCE:,.2f}")
    print(f"Конечный баланс: ${final_balance:,.2f}")
    print(f"Прибыль: ${final_balance - INITIAL_BALANCE:,.2f}")

    # График
    bt["equity_%"] = bt["ret_%"].cumsum()
    plt.figure(figsize=(12, 6))
    plt.plot(bt["signal_time"], bt["equity_%"], linewidth=2, color='blue')
    plt.title(f"Volume Strategy (2020+) | {SYMBOL} | {len(bt)} trades | {total_return:.1f}%")
    plt.xlabel("Date")
    plt.ylabel("Equity %")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    # plt.savefig('backtest_2020.png', dpi=300, bbox_inches='tight')
    # print(f"\nГрафик сохранен как: backtest_2020.png")

if __name__ == "__main__":
    main()
