'''
Script di supporto per testare gli analizzatori sviluppati.
'''

import backtrader as bt
from datetime import datetime
from extensions.analyzers import pivotPointAnalyzer
from extensions.misc.datafeeds import OandaCSVMidData

# Crea un'istanza di cerebro
cerebro = bt.Cerebro()


data = OandaCSVMidData(dataname='data/fx/GBP_USD-2005-2017-D1.csv',
                            timeframe=bt.TimeFrame.Days,
                            compression=1)

cerebro.adddata(data)

cerebro.addanalyzer(pivotPointAnalyzer)

# Esecuzione del backtest e restituzione di un elenco di oggetti strategy
stratList = cerebro.run()

# Ottenere il primo oggetto dell'elenco
strat = stratList[0]

for x in strat.analyzers:
    x.print()

cerebro.plot(style='candlestick')