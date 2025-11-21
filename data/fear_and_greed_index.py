import requests
import pandas as pd

def get():
    response = requests.get("https://api.alternative.me/fng/?limit=0&format=json").json()
    fear_greed_data = response['data']
# Преобразуем в DataFrame для удобства
    fear_greed_df = pd.DataFrame(fear_greed_data, columns=['timestamp', 'value']).set_index('timestamp')
    fear_greed_df.index = pd.to_datetime(fear_greed_df.index, unit='s')
    print(fear_greed_data)

if __name__ == '__main__':
    get()
