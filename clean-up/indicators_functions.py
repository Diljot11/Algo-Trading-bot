# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 12:20:33 2022

@author: singh
"""

#functions of indicators 

import pandas_datareader as pdr
import pandas
import datetime
ticker ="MSFT"

ohlcv= pdr.get_data_yahoo(ticker,datetime.date.today() - datetime.timedelta(1825),datetime.date.today())

def SMA(DF,n):
    df=DF.copy()
    df['sma']=df['Close'].rolling(n).mean()
    df.dropna(inplace=True)
    return df
def EMA(DF,n):
    df=DF.copy()
    df['ema']=df['Close'].ewm(span=n,adjust=False).mean()
    df.dropna(inplace=True)
    return df

#---------------------------------------------------------------------------------------

def MACD(DF,a,b,c):
    df= DF.copy()
    df['ma_fast'] = df ['Adj Close'].ewm(span=a,min_periods=a).mean()
    df['ma_slow'] = df ['Adj Close'].ewm(span=b,min_periods=b).mean()
    df['macd']= df['ma_fast'] - df['ma_slow']
    df['signal'] = df ['macd'].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace = True)
    print(df)
    return df

MACD(ohlcv,12,26,9)

#---------------------------------------------------------------------------------------

def ATR(DF,n):
    df=DF.copy()
    
    df['H_L'] = abs(df['High'] - df['Low'])
    df['H_PC'] = abs(df['High'] - df['Adj Close'].shift(1))
    df['L_PC'] = abs(df['Low'] - df['Adj Close'])
    df['TR'] = df[['H_L','H_PC','L_PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df2=df.drop(['H_L','H_PC','L_PC'],axis=1)
    return df2
ATR(ohlcv,20)
    
#---------------------------------------------------------------------------------------

def VWAP(DF):
    df=DF.copy()
    df['TP'] = abs(df['High'] + df['Low'] + df['Close'])/3
    df['TPV'] = df['TP']*df['Volume']
    df['CPV'] = df['TPV'].shift(1)+ df['TPV'] #cpv=cummulative price*volume
    df['CV'] = df['Volume'] + df['Volume'].shift(1) #cv=cummulative volume
    df['Vwap'] = (df['CPV'])/(df['CV'])
    return df
VWAP(ohlcv)


#---------------------------------------------------------------------------------------


from stocktrends import Renko

def Renko_dataframe(DF):
    df = DF.copy()
    df.reset_index(inplace=True)
    df=df.iloc[:,[0,1,2,3,5,6]]
    df.columns= ["date","open","high","low","close","volume"]

    renko_df= Renko(df)
    renko_df.brick_size=round(ATR(ohlcv,120)["ATR"][-1])
    df2=renko_df.get_ohlc_data()
    print(DF)
    print(df)
    print(df2)
    return df2
renko=Renko_dataframe(ohlcv)




def CAGR(DF):
    df=DF.copy()
    df["daily_ret"] = DF["Adj Close"].pct_change()
    df["cum_return"]=(1+df["daily_ret"]).cumprod()
    n=len(df)/252
    CAGR=(df["cum_return"][-1]**(1/n)-1)
    return CAGR
CAGR(ohlcv)



















    