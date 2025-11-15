
# def calculate_indicators(df, params):
#     df['range'] = df['high'] - df['low']
#     df['atr'] = df['range'].rolling(params['volatility_period']).mean()
#     df['volume_ma'] = df['volume'].rolling(params['volatility_period']).mean()
#     df['upper_band'] = df['close'] + params['multiplier'] * df['atr']
#     df['lower_band'] = df['close'] - params['multiplier'] * df['atr']
#     return df
#
# def generate_signals(df, params):
#     df['signal'] = 0
#     long_cond = (
#         (df['close'] > df['upper_band'].shift()) &
#         (df['volume'] > params['min_volume'] * df['volume_ma'])
#     )
#     short_cond = (
#         (df['close'] < df['lower_band'].shift()) &
#         (df['volume'] > params['min_volume'] * df['volume_ma'])
#     )
#     df.loc[long_cond, 'signal'] = 1
#     df.loc[short_cond, 'signal'] = -1
#     return df

# def calculate_indicators(df, params):
#     """
#     Расчет индикаторов из Strategy002.py
#     """
#     # RSI
#     delta = df['close'].diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
#     rs = gain / loss
#     df['rsi'] = 100 - (100 / (1 + rs))
#     
#     # EMA
#     df['ema12'] = df['close'].ewm(span=12).mean()
#     df['ema26'] = df['close'].ewm(span=26).mean()
#     
#     # MACD
#     df['macd'] = df['ema12'] - df['ema26']
#     df['macdsignal'] = df['macd'].ewm(span=9).mean()
#     df['macdhist'] = df['macd'] - df['macdsignal']
#     
#     # SMA
#     df['sma50'] = df['close'].rolling(window=50).mean()
#     df['sma200'] = df['close'].rolling(window=200).mean()
#     
#     # Volume SMA
#     df['volume_sma'] = df['volume'].rolling(window=20).mean()
#     
#     return df
#
#
# def generate_signals(df, params):
#     """
#     Генерация сигналов из Strategy002.py
#     """
#     df['signal'] = 0
#     
#     # Условия для LONG (покупки)
#     long_condition = (
#         (df['rsi'] > 30) &
#         (df['macd'] > df['macdsignal']) &
#         (df['close'] > df['sma200']) &
#         (df['volume'] > df['volume_sma'] * 0.8)
#     )
#     
#     # Условия для SHORT (продажи)
#     short_condition = (
#         (df['rsi'] < 70) &
#         (df['macd'] < df['macdsignal']) &
#         (df['close'] < df['sma200']) &
#         (df['volume'] > df['volume_sma'] * 0.8)
#     )
#     
#     # Присваиваем сигналы
#     df.loc[long_condition, 'signal'] = 1
#     df.loc[short_condition, 'signal'] = -1
#     
#     return df

