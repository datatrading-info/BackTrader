
def size_position(self, price, stop, risk, method=0, exchange_rate=None, JPY_pair=False):
    '''
    Funzione di supporto per calcolare la dimensione della posizione
    data una quantità nota di rischio.

    *Args*
    - price: Float, il prezzo corrente dello strumento
    - stop: Float, livello di prezzo dello stop loss
    - risk: Float, l'ammontare del capitale da rischiare

    *Kwarg*
    - JPY_pair: Bool, se lo strumento negoziato fa parte di una coppia JPY. Il moltiplicatore
     utilizzato per i calcoli verrà modificato di conseguenza.
    - method: Int,
        - 0: la valuta Acc e la controvaluta coincidono
        - 1: la valuta Acc è la stessa della valuta di base
        - 2: la valuta Acc non è la stessa della valuta di base o della controvaluta
    - exchange_rate: Float, è il tasso di cambio tra la valuta del conto e la controvaluta.
      Obbligatorio per il metodo 2.
    '''

    if JPY_pair == True:  # Controllo se il cross contiene lo YEN e quindi modificare il multiplicatore
        multiplier = 0.01
    else:
        multiplier = 0.0001

    # Calcolo della quantità da rischiare
    acc_value = self.broker.getvalue()
    cash_risk = acc_value * risk
    stop_pips_int = abs((price - stop) / multiplier)
    pip_value = cash_risk / stop_pips_int

    if method == 1:
        # pip_value = pip_value * price
        units = pip_value / multiplier
        return units

    elif method == 2:
        pip_value = pip_value * exchange_rate
        units = pip_value / multiplier
        return units

    else:  # se method=0
        units = pip_value / multiplier
        return units