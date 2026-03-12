import yfinance as yf
import pandas as pd
import ta

symbols = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "BTCUSD": "BTC-USD"
}

def get_data(symbol):
    df = yf.download(symbol, interval="5m", period="2d", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df["rsi"] = ta.momentum.RSIIndicator(df["Close"], 14).rsi()

    df["jaw"] = df["Close"].rolling(13).mean().shift(8)
    df["teeth"] = df["Close"].rolling(8).mean().shift(5)
    df["lips"] = df["Close"].rolling(5).mean().shift(3)

    stoch = ta.momentum.StochasticOscillator(df["High"], df["Low"], df["Close"])
    df["stoch"] = stoch.stoch()

    macd = ta.trend.MACD(df["Close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    df.dropna(inplace=True)
    return df


def analyze(pair, yf_symbol):

    df = get_data(yf_symbol)
    last = df.iloc[-1]

    price = float(last["Close"])
    rsi = float(last["rsi"])
    stoch = float(last["stoch"])
    jaw = float(last["jaw"])
    teeth = float(last["teeth"])
    lips = float(last["lips"])
    macd = float(last["macd"])
    macd_signal = float(last["macd_signal"])

    uptrend = price > lips > teeth > jaw
    downtrend = price < lips < teeth < jaw

    call_score = 0
    put_score = 0

    if uptrend:
        call_score += 1
    if downtrend:
        put_score += 1

    if rsi < 40:
        call_score += 1
    if rsi > 60:
        put_score += 1

    if stoch < 30:
        call_score += 1
    if stoch > 70:
        put_score += 1

    if macd > macd_signal:
        call_score += 1
    if macd < macd_signal:
        put_score += 1

    signal = "HOLD"
    strength = ""

    if call_score >= 2:
        signal = "BUY"
        strength = ["WEAK","MEDIUM","STRONG","STRONG"][call_score-1]

    elif put_score >= 2:
        signal = "SELL"
        strength = ["WEAK","MEDIUM","STRONG","STRONG"][put_score-1]

    return {
        "pair": pair,
        "price": price,
        "signal": signal,
        "strength": strength
    }