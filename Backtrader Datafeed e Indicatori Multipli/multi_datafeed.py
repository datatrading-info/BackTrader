import backtrader as bt
from datetime import datetime


class maCross(bt.Strategy):
    '''
    Il blog ufficiale di backtrader su questo argomento, è disponibile:
    https://www.backtrader.com/blog/posts/2017-04-09-multi-example/multi-example.html

    oneplot = Forza la visualizzazione di tutti i dati sullo stesso grafico
    '''
    params = (
    ('sma1', 40),
    ('sma2', 200),
    ('oneplot', True)
    )

    def __init__(self):
        '''
        Crea un dizionario di indicatori in modo da poter aggiungere dinamicamente
        gli indicatori alla strategia utilizzando un ciclo. In questo modo la
        strategia funzionerà con qualsiasi numero di feed di dati.
        '''
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['sma1'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.sma1)
            self.inds[d]['sma2'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.sma2)
            self.inds[d]['cross'] = bt.indicators.CrossOver(self.inds[d]['sma1'],self.inds[d]['sma2'])

            if i > 0: # Controllo se non siamo nel primo loop del data feed:
                if self.p.oneplot == True:
                    d.plotinfo.plotmaster = self.datas[0]

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            if not pos:  # nessuna posizione / nessun ordine
                if self.inds[d]['cross'][0] == 1:
                    self.buy(data=d, size=1000)
                elif self.inds[d]['cross'][0] == -1:
                    self.sell(data=d, size=1000)
            else:
                if self.inds[d]['cross'][0] == 1:
                    self.close(data=d)
                    self.buy(data=d, size=1000)
                elif self.inds[d]['cross'][0] == -1:
                    self.close(data=d)
                    self.sell(data=d, size=1000)

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))


class OandaCSVData(bt.feeds.GenericCSVData):
    params = (
        ('nullvalue', float('NaN')),
        ('dtformat', '%Y-%m-%dT%H:%M:%S.%fZ'),
        ('datetime', 6),
        ('time', -1),
        ('open', 5),
        ('high', 3),
        ('low', 4),
        ('close', 1),
        ('volume', 7),
        ('openinterest', -1),
    )


# Capitale iniziale
startcash = 10000

# Creo un'istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungo la strategia
cerebro.addstrategy(maCross, oneplot=False)

# Creo la lista di datafeed
datalist = [
    ('data/CAD_CHF-2005-2017-D1.csv', 'CADCHF'), #[0] = Data file, [1] = Data name
    ('data/EUR_USD-2005-2017-D1.csv', 'EURUSD'),
    ('data/GBP_AUD-2005-2017-D1.csv', 'GBPAUD'),
]

# Ciclo la lista per aggiungere i datafeed in cerebro.
for i in range(len(datalist)):
    data = OandaCSVData(dataname=datalist[i][0])
    cerebro.adddata(data, name=datalist[i][1])


# Imposto il capitale iniziale in cerebro
cerebro.broker.setcash(startcash)

# Esecuzione backtest
cerebro.run()

# Valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa del valore finale
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')