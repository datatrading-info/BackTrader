import backtrader as bt
from datetime import datetime

class TestStrategy(bt.Strategy):

    params = (('percents', 0.9),) # Float: 1 == 100%

    def __init__(self):
        print('-'*32,' STRATEGY INIT ','-'*32)
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        date = self.data.datetime.date()
        close = self.data.close[0]

        print('{}: Close: ${}, Position Size: {}'.format(date, close, self.position.size))

        if not self.position:
            long_tp = close + 50
            long_stop = close - 50
            if date == datetime(2018,1,11).date():
                # Entrata con un ordine a mercato
                # Posizionare il TP a 50 dollari sopra
                buy_ord = self.buy_bracket(limitprice=long_tp, stopprice=long_stop, exectype=bt.Order.Market)

            elif date == datetime(2018,1,21).date():
                # Entrata con un ordine limite per andare short e cattuare il prezzo vicino al massimo
                entry = 200
                short_tp = entry - 50
                short_stop = entry + 50
                buy_ord = self.sell_bracket(limitprice=short_tp, price=entry, stopprice=short_stop, exectype=bt.Order.Stop)


            elif date == datetime(2018,2,11).date():
                # Entrata con un ordine stop per andare short e cattuare il prezzo in discesa
                entry = 290
                short_tp = entry - 50
                short_stop = entry + 50
                buy_ord = self.sell_bracket(limitprice=short_tp, price=entry, stopprice=short_stop, exectype=bt.Order.Limit)

            elif date == datetime(2018,3,23).date():
                # Test Ordine non valido
                # Tentativo di impostare di nuovo un ordine limite
                #   1. Exetype non corretto
                #   2. Valore Stop inferiore al prezzo (non corretto per lo short)
                #   3. Ordine Limite superiore al prezzo (non corretto per lo short)
                entry = 290
                short_tp = 300
                short_stop = 90
                buy_ord = self.sell_bracket(limitprice=short_tp, price=entry, stopprice=short_stop, exectype=bt.Order.Stop)


    def notify_order(self, order):
        date = self.data.datetime.datetime().date()

        if order.status == order.Accepted:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('Order Accepted')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))


        if order.status == order.Completed:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('Order Completed')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
            print('Created: {} Price: {} Size: {}'.format(bt.num2date(order.created.dt), order.created.price,order.created.size))
            print('-'*80)

        if order.status == order.Canceled:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('Order Canceled')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))

        if order.status == order.Rejected:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('WARNING! Order Rejected')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
            print('-'*80)

    def notify_trade(self, trade):
        date = self.data.datetime.datetime()
        if trade.isclosed:
            print('-'*32,' NOTIFY TRADE ','-'*32)
            print('{}, Close Price: {}, Profit, Gross {}, Net {}'.format(
                                                date,
                                                trade.price,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))
            print('-'*80)

startcash = 10000

# Creazione istanza cerebro
cerebro = bt.Cerebro()

# Aggiungere strategia
cerebro.addstrategy(TestStrategy)

# Creazione data feed
data = bt.feeds.GenericCSVData(
    timeframe=bt.TimeFrame.Days,
    compression=1,
    dataname='data/TestBrackets.csv',
    dtformat=('%m/%d/%Y'),
    datetime=0,
    time=-1,
    high=1,
    low=-1,
    open=1,
    close=1,
    volume=-1,
    openinterest=-1 #-1 significa non usato
    )

# Aggiungere i dati
cerebro.adddata(data)

# Impostazione del capitale iniziale
cerebro.broker.setcash(startcash)

# Esecuzione del backtest
cerebro.run()

# Valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Grafico dei risultati
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))