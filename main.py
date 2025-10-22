# -- coding: utf-8 --
from binance.client import Client
import config
import utils 



client = Client(config.CONTAS[0]['API_KEY'],
        config.CONTAS[0]['API_SECRET'],
        {"timeout": 40})


INFO = client.futures_symbol_ticker()



for ativo in INFO:
        
    try:
        neg_key = False
        pos_key = False
        #Agora eu pego o DataFrame da moeda
        #e iremos fazer a análise em cima dele
        df = utils.get_all_binance(
                                ativo['symbol'],
                                '5m',
                                client)
        
        
        
        df.to_csv("./data_source/{}.csv".format(ativo['symbol']))
        break
    except Exception as z:
        print(z)