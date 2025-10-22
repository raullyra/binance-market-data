import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import os
from matplotlib import ticker

# ---------- 1. Configuração Inicial ----------
output_dir = "C:/Users/PC02/Set/graph_outputs"
os.makedirs(output_dir, exist_ok=True)  # Cria a pasta se não existir
plt.style.use('seaborn-v0_8-whitegrid')  # Estilo moderno para os gráficos

# ---------- 2. Ler e Preparar Dados ----------
def carregar_dados(caminho_csv):
    """Carrega e prepara os dados do CSV"""
    df = pd.read_csv(caminho_csv)
    
    # Verificar dados
    print("\nPrimeiras linhas do DataFrame:")
    print(df.head())
    
    # Converter para datetime e ajustar colunas
    df['Date'] = pd.to_datetime(df['timestamp'])
    df.set_index('Date', inplace=True)
    df_candle = df[['open', 'high', 'low', 'close', 'volume']].copy()
    df_candle.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    return df_candle

# ---------- 3. Gráfico Candlestick Melhorado ----------
def plot_candlestick(df, periodo=200, output_path=None):
    """Gera e salva gráfico candlestick profissional"""
    try:
        df_reduzido = df.tail(periodo)
        
        # Configurações avançadas do candlestick
        mc = mpf.make_marketcolors(
            up='#2e7d32',  # verde para alta
            down='#c62828',  # vermelho para baixa
            wick={'up':'#2e7d32', 'down':'#c62828'},
            edge={'up':'#2e7d32', 'down':'c62828'},
            volume='in'
        )
        
        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='--',
            gridcolor='#f0f0f0',
            facecolor='white'
        )
        
        mpf.plot(
            df_reduzido,
            type='candle',
            volume=True,
            style=s,
            title=f'Candlestick (Últimos {periodo} períodos)',
            figratio=(12, 6),
            datetime_format='%d/%m %H:%M',
            warn_too_much_data=10000,
            savefig=output_path if output_path else None,
            tight_layout=True,
            scale_padding={'left': 0.3, 'right': 0.3, 'top': 0.5, 'bottom': 0.5}
        )
        
        if output_path:
            print(f"\nCandlestick salvo em: {output_path}")
        return True
    except Exception as e:
        print(f"\nErro no Candlestick: {e}")
        return False

# ---------- 4. Gráfico Renko Profissional ----------
def calcular_renko(df, brick_size=None, periodo=None):
    """Calcula os blocos Renko de forma eficiente"""
    if periodo:
        df = df.tail(periodo)
    
    if brick_size is None:
        # Calcula automaticamente o tamanho do bloco baseado na volatilidade
        brick_size = (df['Close'].max() - df['Close'].min()) / 20
    
    close = df['Close'].values
    renko_prices = [close[0]]
    
    for price in close[1:]:
        while price >= renko_prices[-1] + brick_size:
            renko_prices.append(renko_prices[-1] + brick_size)
        while price <= renko_prices[-1] - brick_size:
            renko_prices.append(renko_prices[-1] - brick_size)
    
    renko_df = pd.DataFrame({'Preço': renko_prices})
    renko_df['Cor'] = ['up' if i == 0 or renko_df['Preço'].iloc[i] >= renko_df['Preço'].iloc[i-1] 
                      else 'down' for i in range(len(renko_df))]
    renko_df.index = pd.date_range(start=df.index[0], periods=len(renko_df), freq='5min')
    
    return renko_df, brick_size

def plot_renko_melhorado(df_renko, brick_size, output_path=None, periodo=None):
    """Gera gráfico Renko profissional com médias móveis"""
    try:
        plt.figure(figsize=(14, 7))
        
        # Configurações estéticas
        colors = {'up': '#2e7d32', 'down': '#c62828'}  # Verde e vermelho mais suaves
        
        # Desenhar cada bloco Renko individualmente
        for i in range(1, len(df_renko)):
            x = df_renko.index[i]
            y_prev = df_renko['Preço'].iloc[i-1]
            y_current = df_renko['Preço'].iloc[i]
            
            # Determinar direção e cor
            if df_renko['Cor'].iloc[i] == 'up':
                color = colors['up']
                bottom = y_prev
            else:
                color = colors['down']
                bottom = y_current
            
            # Desenhar o bloco
            plt.bar(
                x=x,
                height=abs(y_current - y_prev),
                bottom=bottom,
                width=0.8,  # Largura mais adequada para visualização
                color=color,
                edgecolor='black',
                linewidth=0.5
            )
        
        # Adicionar médias móveis (Dica 3)
        df_renko['MA_10'] = df_renko['Preço'].rolling(10).mean()
        df_renko['MA_20'] = df_renko['Preço'].rolling(20).mean()
        
        plt.plot(df_renko.index, df_renko['MA_10'], color='#1565c0', linewidth=1.5, label='MM 10')
        plt.plot(df_renko.index, df_renko['MA_20'], color='#7b1fa2', linewidth=1.5, label='MM 20')
        
        # Ajustes do gráfico
        title = f'Gráfico Renko - Bloco: {brick_size:.6f}'
        if periodo:
            title += f' (Últimos {periodo} períodos)'
            
        plt.title(title, pad=20, fontsize=14)
        plt.xlabel('Data', fontsize=12)
        plt.ylabel('Preço', fontsize=12)
        plt.legend()
        
        # Formatar eixo X (datas)
        plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(10))  # Limitar número de labels
        plt.xticks(rotation=45, ha='right')
        
        # Ajustar margens
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Gráfico Renko salvo em: {output_path}")
            plt.close()
        else:
            plt.show()
        return True
    except Exception as e:
        print(f"\nErro no Renko: {e}")
        return False

# ---------- 5. Execução Principal ----------
def main():
    caminho_csv = "C:/Users/PC02/Set/data_source/ANKRUSDT.csv"
    
    # Carregar dados
    df_candle = carregar_dados(caminho_csv)
    
    # Gerar Candlestick (últimos 200 períodos)
    plot_candlestick(
        df_candle,
        periodo=200,
        output_path=os.path.join(output_dir, 'candlestick_pro.png')
    )
    
    # Gerar Renko (Dica 1 - período específico)
    periodo_renko = 500  # Últimos 500 períodos
    df_renko, brick_size = calcular_renko(
        df_candle,
        brick_size=None,  # Calcula automaticamente
        periodo=periodo_renko
    )
    
    # Plotar Renko com médias móveis (Dica 3)
    plot_renko_melhorado(
        df_renko,
        brick_size,
        output_path=os.path.join(output_dir, 'renko_pro.png'),
        periodo=periodo_renko
    )
    
    print("\nProcesso concluído. Verifique a pasta de saída!")

if __name__ == "__main__":
    main()