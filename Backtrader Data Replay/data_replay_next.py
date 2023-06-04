
def __init__(self):
    # Per tracciare timeframe alti
    self.last_bar = len(self)

def next(self):
    bar = len(self)

    # Controllo se non abbiamo posizioni aperte e abbiamo una barra sul timeframe alto.
    if not self.position and bar > self.last_bar:
        pass

    self.last_bar = bar