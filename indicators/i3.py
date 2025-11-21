import pandas as pd

def calculate_indicators(df, params):
    """
    Расчет индикаторов для стратегии объема
    """
    # Параметры из стратегии
    volume_lookback = params.get('volume_lookback', 60)
    
    # Средний объем за последние N периодов
    df['volume_ma'] = df['volume'].rolling(window=volume_lookback).mean()
    
    # Определяем красные свечи (цена закрытия ниже цены открытия)
    df['is_red'] = df['close'] < df['open']
    # print(df)
    
    return df

def generate_signals(df, params):
    """
    Генерация сигналов как в оригинальной стратегии
    """
    df['signal'] = 0
    
    volume_multiplier = params.get('volume_multiplier', 2.0)
    volume_lookback = params.get('volume_lookback', 60)
    
    # Проходим по всем свечам как в оригинальном бэктесте
    for i in range(volume_lookback, len(df) - 1):
        current = df.iloc[i]
        print(current)
        
        # Проверяем условия для текущей свечи
        is_red = current['close'] < current['open']
        vol_ok = current['volume'] >= volume_multiplier * current['volume_ma']
        
        # Если условия выполнены, ставим сигнал на СЛЕДУЮЩЕЙ свече
        if is_red and vol_ok:
            df.at[df.index[i + 1], 'signal'] = 1
    
    return df
