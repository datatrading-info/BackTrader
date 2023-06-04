
import backtrader as bt
from datetime import datetime

# Creare un istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungere una strategy
cerebro.addstrategy(bt.Strategy)

data = bt.feeds.Quandl(
    dataname='TSLA',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True,
    )

# Filtro sui dati
data.addfilter(bt.filters.HeikinAshi(data))

# Aggiungere i dati a Cerebro
cerebro.adddata(data)

# Esecuzione del backtest
cerebro.run()

# Grafico dei risultati finali
cerebro.plot(style='candlestick')