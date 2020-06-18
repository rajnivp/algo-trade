import investpy
from dateutil.relativedelta import relativedelta
from datetime import date


def get_date(interval=180):
    """
    This function takes interval as its argument
    and return dates with gap of interval
    """
    current_date = date.today()
    end_date = current_date.strftime("%d/%m/%Y")
    start_date = current_date - relativedelta(days=interval)
    start_date = start_date.strftime("%d/%m/%Y")
    return start_date, end_date


def get_current_data(symbol):
    """
    Function returns stock data of latest trading day for given stock symbol
    """
    try:
        day_data = investpy.get_stock_recent_data(symbol, "india")
        current_day_data = day_data.iloc[-1]
        return current_day_data

    except IndexError:
        return False


def get_frame_data(symbol, start_date, end_date):
    """
    This function return data frame consisting of stock data
    in range of given dates for given stock symbol
    """
    try:
        data = investpy.get_stock_historical_data(stock=symbol, country="india", from_date=start_date,
                                                  to_date=end_date)
        return data

    except IndexError:
        return False


def get_data(symbol, start_date, end_date):
    """
    This function returns data frame consisting of stock data between given dates,
    data for last trading day in given date range and data for second last trading day.
    so those data can use to apply various comparision filters for day data and long term data
    """
    try:
        data = investpy.get_stock_historical_data(stock=symbol, country="india", from_date=start_date,
                                                  to_date=end_date)
        day_data = data.iloc[-1]
        prev_day_data = data.iloc[-2]
        return data, day_data, prev_day_data

    except IndexError:
        return (None, None, None)


def average_volume(symbol, start_date, end_date):
    """
    Returns average volume for a stock in given date range
    """
    data = get_frame_data(symbol, start_date, end_date)
    avg_vol = data["Volume"].mean()
    return avg_vol


def volatility(symbol, start_date, end_date):
    """
    Returns average volatility for a stock in given date range
    """
    data = get_frame_data(symbol, start_date, end_date)
    vix = ((data["High"] - data["Low"]) / data["Low"]) * 100
    vix = vix.mean()
    return vix


def traded_value(symbol, start_date, end_date):
    """
    Returns average trade value for a stock in given date range
    """
    data = get_frame_data(symbol, start_date, end_date)
    value = (data["Volume"] * data["Close"]).mean()
    return value


def price_movement(symbol, start_date, end_date):
    """
    Returns percentage price changes for a stock in given date range
    """
    data = get_frame_data(symbol, start_date, end_date)
    price_change = ((data["Close"] - data["Close"].shift(1)) / data["Close"].shift(1)) * 100
    price_change = round(price_change.fillna(value=0), 2)
    return price_change


class Filter:
    """
    Filter class takes symbol ,start date and end date as parameters
    and get data for that parameters and derives price ,volume data from it
    if data returned successfully
    """

    def __init__(self, symbol, start_date, end_date):

        self.symbol = symbol
        try:
            self.data, self.day_data, self.prev_day_data = get_data(self.symbol, start_date, end_date)
            self.avg_vol = self.data["Volume"].mean()
            self.day_vol = self.day_data["Volume"]
            self.day_close = self.day_data["Close"]
            self.day_high = self.day_data["High"]
            self.day_low = self.day_data["Low"]
            self.prev_close = self.prev_day_data["Close"]

        except TypeError:
            pass

    def filter_by_volume(self, multiplier):
        """
        This function takes multiplier as argument
        and it will be used to compare if day volume with average volume multiplied by multiplier
        for example if multiplier is 2 then function return true if day volume is double or more
        than double in comparison to average volume
        """
        try:
            if self.day_vol >= self.avg_vol * multiplier:
                return True

            return False

        except AttributeError:
            return False

    def filter_by_value(self, value):
        """
        This function will check if turnover for a day is more than given value
        """
        try:
            turnover = self.day_close * self.day_vol
            if turnover >= value:
                return True

            return False

        except AttributeError:
            return False

    def filter_by_volatility(self, day_vix):
        """
        This function will check if volatility for day is more than volatility provided in argument
        """
        try:
            vix = ((self.day_high - self.day_low) / self.day_low) * 100
            if vix >= day_vix:
                return True

            return False

        except AttributeError:
            return False

    def filter_by_price_change(self, price_change):
        """
        This function will check if percentage price change is more than given price change in argument
        """
        try:
            price_change_perc = ((self.day_close - self.prev_close) / self.prev_close) * 100
            if abs(price_change_perc) >= price_change:
                return True

            return False

        except AttributeError:
            return False


class Layers(Filter):
    """
    Layers class inherited from Filter class
    it will be used to define various filter layers through which data we get in Filter class will pass
    and will return filtered  data if it pass successfully from all conditionals functions
    """

    def __init__(self, symbol, start_date, end_date):
        super().__init__(symbol, start_date, end_date)

    def layer_1(self):
        """
        Returns data if it passes given chained conditions
        """
        if self.filter_by_volume(multiplier=2) and self.filter_by_volatility(day_vix=3) and self.filter_by_value(
                value=2e9):
            return self.data

    def layer_2(self):
        """
        Returns data if it passes given nested chained conditions
        """
        if self.filter_by_value(value=2e8):
            if self.filter_by_value(value=5e9):
                if self.filter_by_volume(multiplier=1.5) and self.filter_by_volatility(day_vix=2.5):
                    return self.data
            elif self.filter_by_value(1e9):
                if self.filter_by_volume(multiplier=2) and self.filter_by_volatility(day_vix=3.33):
                    return self.data
            else:
                if self.filter_by_volume(multiplier=2.5) and self.filter_by_volatility(day_vix=4):
                    return self.data
