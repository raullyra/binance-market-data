from binance.client import Client
import pandas as pd
from datetime import datetime

API_KEY = 'n4nUqyhwpPFB5p8cVg2FZWci1vdIFr6xjQSYfujoJJkV0FNqCYWc3dvawb9mSIsE'
API_SECRET = 'QlNPRnQcKX2nV0kz4jepQcruVdMDdS8sYAip42zyD19mRdWaIxVVzcIz8S9vijJo'

client = Client(API_KEY, API_SECRET)

def get_daily_data(symbol='BTCUSDT', limit=1):
    klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]

# --- Obter lista de pares USDT ---
tickers = client.get_all_tickers()
symbols = [t['symbol'] for t in tickers if t['symbol'].endswith('USDT')]

# --- Coletar dados de todos ---
dados = []
for s in symbols:
    try:
        df_temp = get_daily_data(s, 1)  # último dia
        last_row = df_temp.iloc[-1]
        dados.append({
            'symbol': s,
            'date': last_row['open_time'],
            'open': last_row['open'],
            'high': last_row['high'],
            'low': last_row['low'],
            'close': last_row['close'],
            'volume': last_row['volume']
        })
    except Exception as e:
        print(f"Erro com {s}: {e}")

df_all = pd.DataFrame(dados)
print(df_all.head())

# --- Salvar arquivo com data ---
hoje = datetime.now().strftime("%Y-%m-%d")
arquivo = f"binance_market_{hoje}.csv"
df_all.to_csv(arquivo, index=False)

print(f"Arquivo salvo: {arquivo}")
