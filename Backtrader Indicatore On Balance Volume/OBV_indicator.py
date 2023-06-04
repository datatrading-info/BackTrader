
import backtrader as bt
from datetime import datetime

class OnBalanceVolume(bt.Indicator):
    '''
    ----------------------------------------------------------------------
    Investopedia:
    ----------------------------------------------------------------------
    https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:on_balance_volume_obv

    1. Se il prezzo di chiusura di ogge è maggiore del prezzo di chiusura di ieri,
       allora: OBV attuale = OBV precedente + il volume di oggi

    2. Se il prezzo di chiusura di ogge è maggiore del prezzo di chiusura di ieri,
       allora: OBV attuale = OBV precedente - il volume di oggi

    3. Se il prezzo di chiusura di ogge è uguale al prezzo di chiusura di ieri,
       allora: OBV attuale = OBV precedente
    ----------------------------------------------------------------------
    '''

    alias = 'OBV'
    lines = ('obv',)

    plotlines = dict(
        obv=dict(
            _name='OBV',
            color='purple',
            alpha=0.50
        )
    )

    def __init__(self):

        # Grafico di una linea orizzontale
        self.plotinfo.plotyhlines = [0]

    def nextstart(self):
        # Dobbiamo usare nextstart per fornire il valore iniziale perché non
        # abbiamo un valore precedente per il primo calcolo.
        # Questi sono noti come valori seed.

        # Creare gli alias
        c = self.data.close
        v = self.data.volume
        obv = self.lines.obv

        if c[0] > c[-1]:
            obv[0] = v[0]
        elif c[0] < c[-1]:
            obv[0] = -v[0]
        else:
            obv[0] = 0

    def next(self):
        # Alias
        c = self.data.close
        v = self.data.volume
        obv = self.lines.obv

        if c[0] > c[-1]:
            obv[0] = obv[-1] + v[0]
        elif c[0] < c[-1]:
            obv[0] = obv[-1] - v[0]
        else:
            obv[0] = obv[-1]


class testStrategy(bt.Strategy):

    def __init__(self):
        self.obv = OnBalanceVolume(self.data)

    def next(self):
        print("{}: Prev: {}: Close: {}, Volume: {} OBV: {}".format(
            self.data.datetime.date(),
            self.data.close[-1],
            self.data.close[0],
            self.data.volume[0],
            self.obv.lines.obv[0]))

# Creao un istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungere la strategia
cerebro.addstrategy(testStrategy)

# Download i dati di Apple da Quandl.
data = bt.feeds.Quandl(
    dataname='AAPL',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True,
    )

# Aggiungere i dati a cerebro
cerebro.adddata(data)

# Esecuzione del backtest
cerebro.run()

# Grafico dei risultati
cerebro.plot(style='candlestick')