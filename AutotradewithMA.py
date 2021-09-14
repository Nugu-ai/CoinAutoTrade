import time
import pyupbit
import datetime
import numpy as np
import schedule

access = "hnijp8VO0cC5Wx09dD2tgyJIeaWfcpqbFxYGj3z8"
secret = "rNP8SbOZwdHVRQIY60WaWIDDnosFSvIGWqSdeUwu"
tick = "KRW-BCHA"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_ror(k, ticker):
    df = pyupbit.get_ohlcv(ticker, count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

bestk = 0.5
def find_bestk(ticker):
    global bestk
    k_ls = []
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k, ticker)
        k_ls.append([k,ror])

    bestk = max(k_ls, key=lambda x: x[1])[0]

find_bestk(tick)
schedule.every().day.hour.do(lambda: find_bestk(tick))

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(tick)
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(tick, bestk)
            ma15 = get_ma15(tick)
            current_price = get_current_price(tick)
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(tick, krw*0.9995)
        else:
            btc = get_balance(tick.split("-")[1])
            if btc > 5000 / current_price:
                upbit.sell_market_order(tick, btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
