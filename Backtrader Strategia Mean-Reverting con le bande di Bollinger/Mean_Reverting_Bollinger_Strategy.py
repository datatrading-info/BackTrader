import backtrader as bt
from datetime import datetime


class BOLLStrat(bt.Strategy):
    '''
    Questa è una semplice strategia mean reversion con le banda di bollinger

    Criteri di ingresso:
        - Long:
            - Il prezzo chiude al di sotto della banda inferiore
            - Ordine Stop di entrata quando il prezzo supera di nuovo la banda inferiore
        - Short:
            - Il prezzo chiude al di sopra della banda superiore
            - Ordine Stop di entrata quando il prezzo torna al di sotto della banda superiore
    Criterio di Uscita
        - Long/Short: il prezzo tocca la linea mediana
    '''

    params = (
        ("period", 20),
        ("devfactor", 2),
        ("size", 20),
        ("debug", False)
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
        # self.sx = bt.indicators.CrossDown(self.data.close, self.boll.lines.top)
        # self.lx = bt.indicators.CrossUp(self.data.close, self.boll.lines.bot)

    def next(self):

        orders = self.broker.get_orders_open()

        # Cancella gli ordini aperti in modo che possiamo seguire la linea mediana
        if orders:
            for order in orders:
                self.broker.cancel(order)

        if not self.position:

            if self.data.close > self.boll.lines.top:
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0], size=self.p.size)

            if self.data.close < self.boll.lines.bot:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0], size=self.p.size)


        else:

            if self.position.size > 0:
                self.sell(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)

            else:
                self.buy(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)

        if self.p.debug:
            print('---------------------------- NEXT ----------------------------------')
            print("1: Data Name:                            {}".format(data._name))
            print("2: Bar Num:                              {}".format(len(data)))
            print("3: Current date:                         {}".format(data.datetime.datetime()))
            print('4: Open:                                 {}'.format(data.open[0]))
            print('5: High:                                 {}'.format(data.high[0]))
            print('6: Low:                                  {}'.format(data.low[0]))
            print('7: Close:                                {}'.format(data.close[0]))
            print('8: Volume:                               {}'.format(data.volume[0]))
            print('9: Position Size:                       {}'.format(self.position.size))
            print('--------------------------------------------------------------------')

    def notify_trade(self, trade):
        if trade.isclosed:
            dt = self.data.datetime.date()

            print('---------------------------- TRADE ---------------------------------')
            print("1: Data Name:                            {}".format(trade.data._name))
            print("2: Bar Num:                              {}".format(len(trade.data)))
            print("3: Current date:                         {}".format(dt))
            print('4: Status:                               Trade Complete')
            print('5: Ref:                                  {}'.format(trade.ref))
            print('6: PnL:                                  {}'.format(round(trade.pnl, 2)))
            print('--------------------------------------------------------------------')


# Capitale iniziale
startcash = 10000

# Creare un'istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungere la strategia
cerebro.addstrategy(BOLLStrat)

data = bt.feeds.Quandl(
    dataname='AMZN',
    fromdate=datetime(2017, 1, 1),
    todate=datetime(2018, 1, 1),
    buffered=True,
)

# Aggiungere i dati storici a Cerebro
cerebro.adddata(data)

# Aggiungere un sizer
cerebro.addsizer(bt.sizers.FixedReverser, stake=10)

# Esecuzione del backtest
cerebro.run()

# Ottenere il valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa dei risultati finali
print('Final Portfolio Value: ${}'.format(round(portvalue, 2)))
print('P/L: ${}'.format(round(pnl, 2)))

# Grafico dei risultati
cerebro.plot(style='candlestick')