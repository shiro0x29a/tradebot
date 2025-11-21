
import pandas as pd
import numpy as np


def backtest(df, initial_balance, risk_per_trade, params, commission_rate=0.001):
    """
    Бэктест стратегии объема из статьи
    Точное повторение логики: вход на открытии следующей свечи, выход на закрытии
    """
    balance = initial_balance
    position = 0
    trade_count = 0
    winning_trades = 0
    entry_price = 0
    total_commission = 0
    
    # Расчет профита холда
    hold_start_price = df.iloc[0]['close']
    hold_end_price = df.iloc[-1]['close']
    hold_profit_pct = (hold_end_price - hold_start_price) / hold_start_price * 100
    hold_profit_usd = initial_balance * (hold_end_price / hold_start_price) - initial_balance
    
    # Проходим по всем свечам (начинаем с 1, т.к. смотрим на предыдущие сигналы)
    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        
        # ОТКРЫТИЕ позиции (если на предыдущей свече был сигнал)
        # if prev['signal'] == 1 and position == 0 and balance > 0:
        if current['signal'] == 1 and position == 0 and balance > 0:
            # ВХОД по цене ОТКРЫТИЯ текущей свечи (как в статье: next_bar["open"])
            entry_price = current['open']
            
            # Расчет размера позиции (фиксированный % от баланса)
            # position_value = balance * risk_per_trade
            position_value = balance
            
            # Проверяем, что хватает средств
            if position_value > 0 and entry_price > 0:
                position_size = position_value / entry_price
                
                # Минимальная проверка размера сделки
                # min_trade_value = 10
                # if position_size * entry_price >= min_trade_value:
                if position_size:
                    position = position_size
                    
                    # Комиссия за открытие
                    commission_open = abs(position * entry_price) * commission_rate
                    if commission_open < balance:
                        balance -= commission_open
                        total_commission += commission_open
                    else:
                        position = 0  # Не хватает на комиссию
    
        # ЗАКРЫТИЕ позиции (если есть открытая позиция)
        if position != 0:
            # Закрываем по цене закрытия текущей свечи (как в статье)
            exit_price = current['close']
            
            # Расчет PnL
            if position > 0:  # Long позиция
                pnl = position * (exit_price - entry_price)
            else:  # Short позиция (в данной стратегии только long)
                pnl = position * (entry_price - exit_price)
            
            # Комиссия за закрытие
            commission_close = abs(position * exit_price) * commission_rate
            pnl -= commission_close
            total_commission += commission_close
            
            # Обновляем баланс
            balance += pnl
            trade_count += 1
            
            # Считаем прибыльные сделки
            if pnl > 0:
                winning_trades += 1
            
            # Закрываем позицию
            position = 0
    # Расчет результатов стратегии
    strategy_profit_pct = (balance - initial_balance) / initial_balance * 100
    strategy_profit_usd = balance - initial_balance
    
    # Расчет годовой доходности
    days_in_test = (df.index[-1] - df.index[0]).days
    if days_in_test > 0:
        annual_return = ((balance / initial_balance) ** (365/days_in_test) - 1) * 100
    else:
        annual_return = 0
    
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
        'winning_trades': winning_trades,
        'win_rate': win_rate,
        'days_in_test': days_in_test,
        'total_commission': total_commission
    }
