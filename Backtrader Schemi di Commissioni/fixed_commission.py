import backtrader as bt

class FixedCommisionScheme(bt.CommInfoBase):
    """
    Questo è un semplice schema di commissioni fisse
    """
    params = (
        ('commission', 5),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
        )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission

# Creo un istanza di cerebro
cerebro = bt.Cerebro()

# Imposto commissioni
comminfo = FixedCommisionScheme()
cerebro.broker.addcommissioninfo(comminfo)