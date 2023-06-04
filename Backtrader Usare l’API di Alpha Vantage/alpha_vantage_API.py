
from alpha_vantage.timeseries import TimeSeries
import argparse
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description='Market Data Downloader')


    parser.add_argument('-s','--symbol',
                        type=str,
                        required=True,
                        help='The Symbol of the Instrument/Currency Pair To Download')

    parser.add_argument('-o', '--outfile',
                        type=str,
                        required=True,
                        help='The output directory and file name to save the data')

    return parser.parse_args()

# Get our arguments
args = parse_args()

print(args)

# Submit our API and create a session
alpha_ts = TimeSeries(key='INSERT YOUR API', output_format='pandas')

# Get the data
data, meta_data = alpha_ts.get_daily(symbol=args.symbol, outputsize='compact')

# Save the data
data.to_csv(args.outfile)