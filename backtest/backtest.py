import pandas as pd
import numpy as np

def backtest(df, initial_balance, risk_per_trade, params, commission_rate=0.0001):
    balance = initial_balance
    position = 0
    trade_count = 0
    winning_trades = 0
    entry_price = 0

    entry_atr = 0
    risk_per_trade = 1
    
    # Расчет профита холда
    hold_start_price = df.iloc[0]['close']
    hold_end_price = df.iloc[-1]['close']
    hold_profit_pct = (hold_end_price - hold_start_price) / hold_start_price * 100
    hold_profit_usd = initial_balance * (hold_end_price / hold_start_price) - initial_balance
    
    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        if position != 0:
            if position > 0:  # Long
                # ПРОДАЕМ по текущей цене закрытия (реальная цена!)
                exit_price = current['close']
                pnl = position * (exit_price - entry_price)
            else:  # Short
                # ПОКУПАЕМ обратно по текущей цене закрытия  
                exit_price = current['close']
                pnl = position * (entry_price - exit_price)

            commission_close = abs(position * exit_price) * commission_rate
            # print(position)
            # print(exit_price)
            # print(commission_close)
            pnl -= commission_close
            
            balance += pnl
            trade_count += 1
            if pnl > 0: winning_trades += 1
            position = 0
        
        if prev['signal'] != 0 and position == 0:
            # Открываем позицию по ЦЕНЕ ЗАКРЫТИЯ того дня, когда получили сигнал
            # entry_price = current['open']
            entry_price = prev['close']
            
            # Простой расчет размера позиции (например, 10% от баланса)
            position_value = balance * risk_per_trade
            position_size = position_value / entry_price
            
            position = position_size if prev['signal'] == 1 else -position_size

            commission_open = abs(position * entry_price) * commission_rate
            balance -= commission_open
    
    # Расчет доходности стратегии
    strategy_profit_pct = (balance - initial_balance) / initial_balance * 100
    strategy_profit_usd = balance - initial_balance
    
    # Расчет годовой доходности
    days_in_test = (df.index[-1] - df.index[0]).days
    annual_return = ((balance / initial_balance) ** (365/days_in_test) - 1) * 100 if days_in_test > 0 else 0
    win_rate = (winning_trades / trade_count * 100) if trade_count > 0 else 0
    
    return {
        'initial_balance': initial_balance,
        'final_balance': balance,
        'strategy_profit_pct': strategy_profit_pct,
        'strategy_profit_usd': strategy_profit_usd,
        'hold_profit_pct': hold_profit_pct,
        'hold_profit_usd': hold_profit_usd,
        'annual_return': annual_return,
        'trades': trade_count,
        'win_rate': win_rate,
        'days_in_test': days_in_test
    }
