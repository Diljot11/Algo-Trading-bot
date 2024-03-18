# -*- coding: utf-8 -*-
# """
# Created on Sat Apr 30 15:20:04 2022

# @author: singh
# """
from alpha_vantage.timeseries import TimeSeries
import pandas
import pandas_datareader
from stocktrends import Renko

ts = TimeSeries(key='RWD1G09NAY3SBZKZ', output_format='pandas')
data = ts.get_intraday(symbol='MSFT', interval='1min', outputsize='full')[0]
data.columns = ["Open", "High", "Low", "Close", "Volume"]



def SMA(DF,n):
    df=DF.copy()
    df['sma']=df['Close'].rolling(n).mean()
    df.dropna(inplace=True)
    return df
sma=SMA(data,10)
print (sma)


def EMA(DF,n):
    df=DF.copy()
    df['ema']=df['Close'].ewm(span=n,adjust=False).mean()
    df.dropna(inplace=True)
    return df
ema=EMA(data,5)
print(ema)

def VWAP(DF):
    df = DF.copy()
    df['TP'] = abs(df['High'] + df['Low'] + df['Close']) / 3
    df['TPV'] = df['TP'] * df['Volume']
    df['CPV'] = df['TPV'].shift(1) + df['TPV']  # cpv=cummulative price*volume
    df['CV'] = df['Volume'] + df['Volume'].shift(1)  # cv=cummulative volume
    df['Vwap'] = (df['CPV']) / (df['CV'])
    return df


vwap = VWAP(data)
print(vwap)


def ATR(DF, n):
    df = DF.copy()
    df['H_L'] = abs(df['High'] - df['Low'])
    df['H_PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L_PC'] = abs(df['Low'] - df['Close'])
    df['TR'] = df[['H_L', 'H_PC', 'L_PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df2 = df.drop(['H_L', 'H_PC', 'L_PC'], axis=1)
    return df2


atr=ATR(data, 20)
# print (atr)
# atr["ATR"].plot()


def Renko_dataframe(DF):
    df = DF.copy()
    df.reset_index(inplace=True)

    # print (df)
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    # print(df)
    df2 = Renko(df)
    print("-----------1--------------")
    print(df2)
    atr = ATR(data, 120)["ATR"][-1]
    print(atr)
    df2.brick_size = round(atr, 1)
    renko_df = df2.get_ohlc_data()
    return renko_df


renko = Renko_dataframe(data)
print("-----------2--------------")
print(renko)
# atr["ATR"].plot()


df = data.copy()
df.reset_index(inplace=True)

df.columns = ["date", "open", "high", "low", "close", "volume"]

df2 = Renko(df)
atr = ATR(data, 120)["ATR"][-1]
print("-------------3-------------")
print(atr)
df2.brick_size = round(atr, 0)


