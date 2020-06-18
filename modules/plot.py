import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt


def candlestick_chart(data, name='Candlestick chart'):
    """
    Plot candlestick chart on given data
    function takes data frame as input and return candlestick chart figure
    """
    # Set candlestick chart style
    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc, gridcolor='k')
    fig, axlist = mpf.plot(data,
                           type='candle',
                           volume=True, style=s,
                           title=name,
                           figratio=(22, 12),
                           figscale=1,
                           returnfig=True
                           )
    return fig, axlist


def rolling_means(df, name="price", window_size=10):
    """
    Plot rolling mean for given data in given window size
    """
    window = window_size

    # Get closing prices from data frame
    roll_mean = pd.Series(df["Close"]).rolling(window).mean()
    roll_std = pd.Series(df["Close"]).rolling(window).std()
    upper_band, lower_band = roll_mean + 2 * roll_std, roll_mean - 2 * roll_std

    fig, ax = plt.subplots(1, 1)
    plt.suptitle("Rolling means")

    ax.plot(df["Close"], label=name)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")

    ax.plot(roll_mean, label="roll means")
    ax.plot(upper_band, label="upper band")
    ax.plot(lower_band, label="lower band")
    ax.legend(loc="upper right")

    plt.margins(x=0)


def variance_indicators(df1, df2=None):
    """
    plot price and cumulative price deviation
    if df2 sets to to data of other data frame then
    comparison charts for those variance will be plotted
    """
    # Get closing prices from data frame
    df1 = df1["Close"]

    dl = ((df1 / df1.shift(1)) - 1) * 100
    dl.iloc[0] = 0
    mean, std, kurt = dl.mean(), dl.std(), dl.kurtosis()
    cumsum = dl.cumsum()

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle("Variance")
    ax1.plot(dl, label="df1")
    ax1.set_ylabel("Price-deviation")
    ax2.plot(cumsum, label='df2')
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Price-deviation-cumulative")

    if df2 is not None:
        df2 = df2["Close"]
        dl1 = ((df2 / df2.shift(1)) - 1) * 100
        dl1.iloc[0] = 0
        mean, std, kurt = dl1.mean(), dl1.std(), dl1.kurtosis()
        cumsum = dl1.cumsum()
        ax1.plot(dl1, label="df2")
        ax2.plot(cumsum, label="df2")

    ax1.legend(loc="upper right")
    ax2.legend(loc="upper right")
    plt.margins(x=0)
