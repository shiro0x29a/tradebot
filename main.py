from data import *
from indicators import *
from backtest import *

symbol = 'BTC/USDT'
symbol = 'ETH/USDT'
# symbol = 'TON/USDT'
timeframe = '1h'
timeframe = '1d'
# timeframe = '5m'
initial_balance = 10000
risk_per_trade = 0.02
start_date = '2023-01-01'
end_date = '2023-01-31'
end_date = '2023-12-31'

start_date = '2020-01-01'
end_date = '2026-12-31'

params = {
    'volatility_period': 20,
    'multiplier': 2.5,
    'take_profit': 1.5,
    'stop_loss': 2.5,   
    'min_volume': 0.5
}

if __name__ == "__main__":
    exchange = ccxt.binance({'enableRateLimit': True})
    
    print("Fetching data...")
    df = fetch_ohlcv(exchange, symbol, timeframe, start_date, end_date)
    
    print("Calculating indicators...")
    df = calculate_indicators(df, params)
    
    print("Generating signals...")
    df = generate_signals(df, params)
    
    print("Starting backtest...")
    results = backtest(df, initial_balance, risk_per_trade, params)
    
    print("\n=== Results ===")
    print(f"Period: {start_date} - {end_date} ({results['days_in_test']} дней)")
    print(f"Timeframe: {timeframe}")
    print("\n=== Strategy ===")
    print(f"Initial balance: ${results['initial_balance']:,.2f}")
    print(f"Final balance: ${results['final_balance']:,.2f}")
    print(f"Profit: ${results['strategy_profit_usd']:,.2f} ({results['strategy_profit_pct']:.2f}%)")
    print(f"APR: {results['annual_return']:.2f}%")
    print(f"Trades: {results['trades']}")
    print(f"Win Rate: {results['win_rate']:.2f}%")
    print("\n=== Buy & Hold ===")
    print(f"Hold profit: ${results['hold_profit_usd']:,.2f} ({results['hold_profit_pct']:.2f}%)")
    print(f"Initial cost: ${df.iloc[0]['close']:,.2f}")
    print(f"Final cost: ${df.iloc[-1]['close']:,.2f}")
