from multiprocessing.dummy import Pool
from threading import Thread
import time
from modules.filter import *
from modules.plot import *


class QuoteGetter(Thread):
    """
    QuoteGetter class will used to get data for thousands of stocks concurrently
    """

    def __init__(self, ticker, start_date, end_date):
        super().__init__()
        self.data = None
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        """
        This function will create object of Layers class and call the layer we want use to filter data
        """
        try:
            layer = Layers(self.ticker, self.start_date, self.end_date)
            self.data = layer.layer_2()

        except (IndexError, AttributeError, TypeError):
            pass


def get_quotes(tickers, start_date, end_date):
    """
    This function will create instances of QuoteGetter class in will run its run method
    and will return dictionary of stock symbols being keys and corresponding stock data being values
    """
    # Create list QuoteGetter instances to run concurrently
    threads = [QuoteGetter(t, start_date, end_date) for t in tickers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    quotes = {ticker: data for ticker, data in zip(tickers, [thread.data for thread in threads]) if data is not None}

    return quotes


def pool_quotes(ticker, start_date, end_date):
    """
    This function will create Layers class object and return data after calling its layer
    this function will used in multiprocessing pooling function
    """
    layer = Layers(ticker, start_date, end_date)
    res = None
    try:
        res = layer.layer_2()

    except (IndexError, AttributeError, TypeError):
        pass

    return res


def pooling(tickers, start_date, end_date):
    """
    Alternative to threading this function can be used
    this function will create pool of processes to run concurrently that will call pool_quotes function
    and will return dictionary of stock symbols being keys and corresponding stock data being values
    """
    # Create list of arguments to pass to pool_quote function
    quotes = [(ticker, start_date, end_date) for ticker in tickers]
    with Pool(10) as pool:
        res = pool.starmap(pool_quotes, quotes)
        pool.close()
        pool.join()

    quotes = {ticker: data for ticker, data in zip(tickers, res) if data is not None}
    return quotes


def main():
    """
    Run filter threads or processes by calling this function
    """
    # Get stock symbols and name
    tickers = pd.read_csv("data/symbols.csv")
    symbols = tickers['symbol']

    # Will use 6 months data
    s, e = get_date(180)

    # To calculate running time
    t0 = time.time()

    # Run threads
    result1 = get_quotes(symbols, s, e)

    # Convert result into pandas data frame
    df = pd.DataFrame({"symbol": list(result1.keys())})

    # Map filtered symbols with names for readability and save it as csv
    filtered = pd.merge(df, tickers, how='inner', on='symbol')
    filtered.to_csv("data/filter.csv", index=False, mode='w')
    run_time = time.time() - t0
    print(run_time)


if __name__ == "__main__":
    main()
