

import backtrader as bt
from datetime import datetime
import math
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Sizers Testing')

    parser.add_argument('--commsizer',
                            action ='store_true',help=('Use the Sizer '
                                'that takes commissions into account'))

    parser.add_argument('--commtype',
                        default="Percentage",
                        type=str,
                        choices=["Percentage", "Fixed"],
                        help='The type of commission to apply to a trade')

    parser.add_argument('--commission',
                        default=0.05,
                        type=float,
                        help='The amount of commission to apply to a trade')

    parser.add_argument('--risk',
                        default=0.01,
                        type=float,
                        help='The percentage of available cash to risk on a trade')

    parser.add_argument('--debug',
                            action ='store_true',
                            help=('Print Sizer Debugs'))

    return parser.parse_args()



class maxRiskSizer(bt.Sizer):
    '''
    Restituisce il numero di azioni arrotondate per difetto che possono essere
    acquistate con la massima tolleranza al rischio
    '''
    params = (('risk', 0.1),
            ('debug', True))

    def _getsizing(self, comminfo, cash, data, isbuy):

        max_risk =  math.floor(cash * self.p.risk)

        if isbuy == True:
            size = max_risk / data[0]
        else:
            size = max_risk / data[0] * -1

        # Arrotodamento per difetto all'intero più vicino
        size = math.floor(size)

        if self.p.debug:
            if isbuy:
                buysell = 'Buying'
            else:
                buysell = 'Selling'
            print("------------- Sizer Debug --------------")
            print("Action: {}".format(buysell))
            print("Price: {}".format(data[0]))
            print("Cash: {}".format(cash))
            print("Max Risk %: {}".format(self.p.risk))
            print("Max Risk $: {}".format(max_risk))
            print("Current Price: {}".format(data[0]))
            print("Size: {}".format(size))
            print("----------------------------------------")
        return size


class maxRiskSizerComms(bt.Sizer):
    '''
    Restituisce il numero di azioni arrotondate per difetto che possono essere
    acquistate con la massima tolleranza al rischio
    '''
    params = (('risk', 0.1),
                ('debug', True))

    def _getsizing(self, comminfo, cash, data, isbuy):
        size = 0

        # Calcola la dimensione massima supponendo che tutta la liquidità può essere usata.
        max_risk = math.floor(cash * self.p.risk)

        comm = comminfo.p.commission

        if comminfo.stocklike: # Usiamo una commissione basata sulla percentuale

            # Applica le commissioni al prezzo. Possiamo quindi dividere il
            # rischio per questo valore
            com_adj_price = data[0] * (1 + (comm * 2)) # *2 for round trip
            comm_adj_max_risk = "N/A"

            if isbuy == True:
                comm_adj_size = max_risk / com_adj_price
                if comm_adj_size < 0: # Evita di andare short accidentalmente
                    comm_adj_size = 0
            else:
                comm_adj_size = max_risk / com_adj_price * -1

        else: # Altrimenti è di dimensioni fisse
            # Decurtare la commissione dalla liquidità disponibile per investire
            comm_adj_max_risk = max_risk - (comm *2) # Round trip
            com_adj_price = "N/A"

            if comm_adj_max_risk < 0: # Liquidità non sufficiente
                return 0

            if isbuy == True:
                comm_adj_size = comm_adj_max_risk / data[0]
            else:
                comm_adj_size = comm_adj_max_risk / data[0] * -1

        # Verifichiamo di arrotondare per difetto all'intero più vicino
        comm_adj_size = math.floor(comm_adj_size)

        if self.p.debug:
            if isbuy:
                buysell = 'Buying'
            else:
                buysell = 'Selling'
            print("------------- Sizer Debug --------------")
            print("Action: {}".format(buysell))
            print("Price: {}".format(data[0]))
            print("Cash: {}".format(cash))
            print("Max Risk %: {}".format(self.p.risk))
            print("Max Risk $: {}".format(max_risk))
            print("Commission Adjusted Max Risk: {}".format(comm_adj_max_risk))
            print("Current Price: {}".format(data[0]))
            print("Commission: {}".format(comm))
            print("Commission Adj Price (Round Trip): {}".format(com_adj_price))
            print("Size: {}".format(comm_adj_size))
            print("----------------------------------------")
        return comm_adj_size

class FixedCommisionScheme(bt.CommInfoBase):
    '''
    Questo è un semplice schema di commissioni fisse
    '''
    params = (
        ('commission', 5),
        ('stocklike', False),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
        )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission

class firstStrategy(bt.Strategy):

    params = (('longshort', False),)

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy()
        elif self.position.size > 0 and self.rsi > 70:
            self.close()
        else:
            pass

args = parse_args()

# Variabile con il capitale iniziale
startcash = 10000

# Creare un istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungo la strategia
cerebro.addstrategy(firstStrategy)

data = bt.feeds.Quandl(
    dataname='F',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True
    )

# Aggiungo i dati finanziari a Cerebro
cerebro.adddata(data)

# Imposto il capitale iniziale
cerebro.broker.setcash(startcash)

# Aggiungo il sizer
if args.commsizer:
    cerebro.addsizer(maxRiskSizerComms, debug=args.debug, risk=args.risk)
else:
    cerebro.addsizer(maxRiskSizer, debug=args.debug, risk=args.risk)


if args.commtype.lower() == 'percentage':
    cerebro.broker.setcommission(args.commission)
else:
    # Aggiungo il nuovo schema delle commissioni
    comminfo = FixedCommisionScheme(commission=args.commission)
    cerebro.broker.addcommissioninfo(comminfo)

# Esecuzione del backtest
cerebro.run()

# Valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa del risultato finale
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')