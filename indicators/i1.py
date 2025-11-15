import pandas as pd
import numpy as np

def calculate_indicators(df, params):
    """
    Расчет индикаторов из pytrader с Ichimoku
    """
    # RSI
    def rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    df['rsi'] = rsi(df['close'])
    
    # Bollinger Bands
    def bollinger_bands(series, period=20, std=2):
        sma = series.rolling(window=period).mean()
        rolling_std = series.rolling(window=period).std()
        upper = sma + (rolling_std * std)
        lower = sma - (rolling_std * std)
        return upper, lower
    
    df['bb_upper'], df['bb_lower'] = bollinger_bands(df['close'])
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    
    # MACD
    def macd(series, fast=12, slow=26, signal=9):
        ema_fast = series.ewm(span=fast).mean()
        ema_slow = series.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    df['macd'], df['macd_signal'], df['macd_hist'] = macd(df['close'])
    
    # SMA
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # Stochastic
    def stochastic(high, low, close, k_period=14, d_period=3):
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        return k, d
    
    df['stoch_k'], df['stoch_d'] = stochastic(df['high'], df['low'], df['close'])
    
    # ATR (Average True Range)
    def atr(high, low, close, period=14):
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
    
    df['atr'] = atr(df['high'], df['low'], df['close'])
    
    # Ichimoku Cloud
    def ichimoku(high, low, close):
        # Conversion Line (Tenkan-sen)
        period9_high = high.rolling(window=9).max()
        period9_low = low.rolling(window=9).min()
        df['tenkan_sen'] = (period9_high + period9_low) / 2
        
        # Base Line (Kijun-sen)
        period26_high = high.rolling(window=26).max()
        period26_low = low.rolling(window=26).min()
        df['kijun_sen'] = (period26_high + period26_low) / 2
        
        # Leading Span A (Senkou Span A)
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        
        # Leading Span B (Senkou Span B)
        period52_high = high.rolling(window=52).max()
        period52_low = low.rolling(window=52).min()
        df['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)
        
        # Lagging Span (Chikou Span)
        df['chikou_span'] = close.shift(-26)
        
        return df
    
    df = ichimoku(df['high'], df['low'], df['close'])
    
    # Volume SMA
    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    
    # Parabolic SAR (упрощенная версия)
    def parabolic_sar(high, low, acceleration=0.02, maximum=0.2):
        sar = [low.iloc[0]]
        ep = high.iloc[0]
        af = acceleration
        
        for i in range(1, len(high)):
            sar_current = sar[-1] + af * (ep - sar[-1])
            
            if sar_current > low.iloc[i]:
                sar_current = low.iloc[i]
            elif sar_current > low.iloc[i-1]:
                sar_current = low.iloc[i-1]
                
            if sar_current < high.iloc[i]:
                sar_current = high.iloc[i]
            elif sar_current < high.iloc[i-1]:
                sar_current = high.iloc[i-1]
                
            if high.iloc[i] > ep:
                ep = high.iloc[i]
                af = min(af + acceleration, maximum)
                
            sar.append(sar_current)
        
        return pd.Series(sar, index=high.index)
    
    df['sar'] = parabolic_sar(df['high'], df['low'])
    
    return df

def generate_signals(df, params):
    """
    Генерация сигналов на основе всех индикаторов
    """
    df['signal'] = 0
    
    # RSI сигналы
    rsi_oversold = params.get('rsi_oversold', 30)
    rsi_overbought = params.get('rsi_overbought', 70)
    
    # Bollinger Bands сигналы
    bb_oversold = (df['close'] < df['bb_lower'])
    bb_overbought = (df['close'] > df['bb_upper'])
    
    # Тренд по SMA
    uptrend = (df['sma_20'] > df['sma_50'])
    downtrend = (df['sma_20'] < df['sma_50'])
    
    # MACD сигналы
    macd_bullish = (df['macd'] > df['macd_signal'])
    macd_bearish = (df['macd'] < df['macd_signal'])
    
    # Stochastic сигналы
    stoch_oversold = (df['stoch_k'] < 20)
    stoch_overbought = (df['stoch_k'] > 80)
    
    # Ichimoku сигналы
    ichimoku_bullish = (
        (df['close'] > df['senkou_span_a']) & 
        (df['close'] > df['senkou_span_b']) &
        (df['tenkan_sen'] > df['kijun_sen'])
    )
    
    ichimoku_bearish = (
        (df['close'] < df['senkou_span_a']) & 
        (df['close'] < df['senkou_span_b']) &
        (df['tenkan_sen'] < df['kijun_sen'])
    )
    
    # Parabolic SAR сигналы
    sar_bullish = (df['close'] > df['sar'])
    sar_bearish = (df['close'] < df['sar'])
    
    # Volume подтверждение
    volume_ok = (df['volume'] > df['volume_sma'])
    
    # # LONG условия (комбинация индикаторов)
    # long_conditions = (
    #     (df['rsi'] > rsi_oversold) & 
    #     (df['rsi'] < rsi_overbought) &
    #     bb_oversold &           # У нижней полосы Боллинджера
    #     uptrend &               # Восходящий тренд
    #     macd_bullish &          # MACD бычий
    #     ichimoku_bullish &      # Ишимоку бычий
    #     sar_bullish &           # SAR бычий
    #     volume_ok               # Объем подтверждает
    # )
    # 
    # # SHORT условия
    # short_conditions = (
    #     (df['rsi'] > rsi_overbought) &
    #     bb_overbought &         # У верхней полосы Боллинджера
    #     downtrend &             # Нисходящий тренд
    #     macd_bearish &          # MACD медвежий
    #     ichimoku_bearish &      # Ишимоку медвежий
    #     sar_bearish &           # SAR медвежий
    #     volume_ok               # Объем подтверждает
    # )
    # 
    # # Присваиваем сигналы
    # df.loc[long_conditions, 'signal'] = 1
    # df.loc[short_conditions, 'signal'] = -1
    # 
    # return df
    conditions_long = {
        'rsi_oversold': df['rsi'] > 30,
        'rsi_not_overbought': df['rsi'] < 70,
        'bb_oversold': df['close'] < df['bb_lower'],
        'uptrend': df['sma_20'] > df['sma_50'],
        'macd_bullish': df['macd'] > df['macd_signal'],
        'ichimoku_bullish': (df['close'] > df['senkou_span_a']) & (df['close'] > df['senkou_span_b']),
        'sar_bullish': df['close'] > df['sar'],
        'volume_ok': df['volume'] > df['volume_sma'] * 0.8
    }
    
    conditions_short = {
        'rsi_overbought': df['rsi'] > 75,  # Обратное условие
        'rsi_not_oversold': df['rsi'] > 30,
        'bb_overbought': df['close'] > df['bb_upper'],
        'downtrend': df['sma_20'] < df['sma_50'],
        'macd_bearish': df['macd'] < df['macd_signal'],
        'ichimoku_bearish': (df['close'] < df['senkou_span_a']) & (df['close'] < df['senkou_span_b']),
        'sar_bearish': df['close'] < df['sar'],
        'volume_ok': df['volume'] > df['volume_sma'] * 0.8
    }
    
    # Подсчитываем количество сработавших условий
    long_score = sum(conditions_long.values())
    short_score = sum(conditions_short.values())
    
    # Минимальное количество условий для сигнала (настраиваемо)
    min_conditions = params.get('min_conditions', 6)
    
    # Генерируем сигналы
    long_signals = (long_score >= min_conditions)
    short_signals = (short_score >= min_conditions)
    
    # Присваиваем сигналы (шорт имеет приоритет при конфликте)
    df.loc[long_signals & ~short_signals, 'signal'] = 1
    df.loc[short_signals & ~long_signals, 'signal'] = -1
    
    # Добавляем отладочную информацию
    df['long_score'] = long_score
    df['short_score'] = short_score
    
    return df

# def generate_signals(df, params):
#     df['signal'] = 0
#     
#     # Условия с весами (важные = 2, обычные = 1)
#     conditions_long = {
#         'rsi_ok': ((df['rsi'] > 30) & (df['rsi'] < 70)) * 2,           # Вес 2
#         'trend_ok': (df['sma_20'] > df['sma_50']) * 2,                 # Вес 2
#         'bb_oversold': (df['close'] < df['bb_lower']) * 1,             # Вес 1
#         'macd_bullish': (df['macd'] > df['macd_signal']) * 1,          # Вес 1
#         'ichimoku_bullish': ((df['close'] > df['senkou_span_a']) & (df['close'] > df['senkou_span_b'])) * 2,  # Вес 2
#         'volume_ok': (df['volume'] > df['volume_sma'] * 0.8) * 1       # Вес 1
#     }
#     
#     conditions_short = {
#         'rsi_ok': ((df['rsi'] > 30) & (df['rsi'] < 70)) * 2,           # Вес 2
#         'trend_ok': (df['sma_20'] < df['sma_50']) * 2,                 # Вес 2
#         'bb_overbought': (df['close'] > df['bb_upper']) * 1,           # Вес 1
#         'macd_bearish': (df['macd'] < df['macd_signal']) * 1,          # Вес 1
#         'ichimoku_bearish': ((df['close'] < df['senkou_span_a']) & (df['close'] < df['senkou_span_b'])) * 2,  # Вес 2
#         'volume_ok': (df['volume'] > df['volume_sma'] * 0.8) * 1       # Вес 1
#     }
#     
#     # Суммируем веса
#     long_score = sum(conditions_long.values())
#     short_score = sum(conditions_short.values())
#     
#     # Минимальный порог (настраиваемо)
#     min_score = params.get('min_score', 8)
#     
#     # Генерируем сигналы
#     long_signals = (long_score >= min_score)
#     short_signals = (short_score >= min_score)
#     
#     df.loc[long_signals & ~short_signals, 'signal'] = 1
#     df.loc[short_signals & ~long_signals, 'signal'] = -1
#     
#     # Отладочная информация
#     df['long_score'] = long_score
#     df['short_score'] = short_score
#     
#     return df
