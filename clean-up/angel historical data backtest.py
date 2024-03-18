# -*- coding: utf-8 -*-
"""
Created on Sat May  7 22:58:02 2022

@author: singh
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May  9 19:07:26 2022

@author: singh
"""


import numpy as np
import pandas as pd
from smartapi import SmartConnect
# import statsmodels.api as sm 
import time
import copy
import requests
import json
obj=SmartConnect(api_key="EK01aqVz")


data = obj.generateSession("D104396","diljot2001")
refreshToken= data['data']['refreshToken']

feedToken=obj.getfeedToken()

userProfile= obj.getProfile(refreshToken)

tickers=["ONGC","SBIN","BRITANNIA","COALINDIA","NTPC","SUNPHARMA","TATASTEEL","ADANIPORTS","M&M","HDFCLIFE","RELIANCE","BAJAJ-AUTO","HINDUNILVR","BPCL","LT","DRREDDY","ICICIBANK","KOTAKBANK","BHARTIARTL","CIPLA","SBILIFE","ASIANPAINT","TATACONSUM","MARUTI","HCLTECH","INDUSINDBK","TCS","TITAN"]



fucks = json.loads(requests.get('https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json').text)
for ticker in tickers:
    for info in fucks :
        if info["exch_seg"] == "NSE":
            if info["symbol"] == ticker +"-EQ":
                print (info["name"], info["symbol"])
        



pos_size=10

# def MACD(DF,a,b,c):
#     df= DF.copy()
#     df['ma_fast'] = df ['Adj Close'].ewm(span=a,min_periods=a).mean()
#     df['ma_slow'] = df ['Adj Close'].ewm(span=b,min_periods=b).mean()
#     df['macd']= df['ma_fast'] - df['ma_slow']
#     df['signal'] = df ['macd'].ewm(span=c,min_periods=c).mean()
#     df.dropna(inplace = True)
#     print(df)
#     return df


def ATR(DF,n):
    df=DF.copy()
    
    df['H_L'] = abs(df['High'] - df['Low'])
    df['H_PC'] = abs(df['High'] - df['Adj Close'].shift(1))
    df['L_PC'] = abs(df['Low'] - df['Adj Close'])
    df['TR'] = df[['H_L','H_PC','L_PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df2=df.drop(['H_L','H_PC','L_PC'],axis=1)
    return df2


# def slope (ser,n):
#     slopes=[i*0 for i in range (n-1)]
#     for i in range (n,len(ser)+1):
#         y=ser[i-n:i]
#         x=np.array(range(n))
#         y_scaled=(y-y.min())/(y.max() - y.min())
#         x_scaled=(x-x.min())/(x.max() - x.min())
#         model=sm.OLS(y_scaled,x_scaled)
#         results=model.fit()
#         slopes.append(results.params[-1])
#     slope_angle=(np.rad2deg(np.arctan(np.array(slope))))
#     return np.array(slope_angle)



# def Renko_dataframe(DF):
#     df = DF.copy()
#     df.reset_index(inplace=True)
#     df=df.iloc[:,[0,1,2,3,5,6]]
#     df.columns= ["date","open","high","low","close","volume"]

#     renko_df= Renko(df)
#     renko_df.brick_size=round(ATR(df,120)["ATR"][-1])
#     df2=renko_df.get_ohlc_data()
#     print(DF)
#     print(df)
#     print(df2)
#     return df2


def VWAP(DF):
    df=DF.copy()
    df['TP'] = abs(df['High'] + df['Low'] + df['Close'])/3
    df['TPV'] = df['TP']*df['Volume']
    df['CPV'] = df['TPV'].shift(1)+ df['TPV'] #cpv=cummulative price*volume
    df['CV'] = df['Volume'] + df['Volume'].shift(1) #cv=cummulative volume
    df['Vwap'] = (df['CPV'])/(df['CV'])
    return df


def renko_merge(DF):
    df=copy.deepcopy(DF)
    
    
    vwap=VWAP(df)
    
    df["date"]=df.index
    
    merged_df=df.merge(vwap.loc[:,["date","Vwap"]],how="outer",on="date")
    # merged_df["bar_num"].fillna(method='ffill',inplace=True)
    # merged_df["macd"]=MACD(merged_df, 12, 26, 9)[0]
    # merged_df["macd_signal"]=MACD(merged_df, 12, 26, 9)[1]
    # merged_df["macd_slope"]= slope(merged_df["macd"],5)
    # merged_df["macd_sig_slope"] = slope(merged_df["macd_sig"],5)
    return merged_df






def trade_signal(merged_df,l_s):
    # function to generate signal 
    
    signal=""
    df=copy.deepcopy(merged_df)
    if l_s == "":
       
                    
        if (df["High"]>= df["VWAP"] and 
            df["Volume"] > 1.5*df["roll_max_vol"].shift(1)) :
                signal="Buy"
        elif df["Low"]<= df["VWAP"] and \
             df["Volume"]>1.5*df["roll_max_vol"]:
                 signal="Sell"
                            
    if l_s == "Buy":
        if df["Low"]<= df["VWAP"] and \
                     df["Volume"]>1.5*df["roll_max_vol"].shift(1):
                         signal="Close_Sell"
        elif df["Close"]< df["Close"]- df["ATR"]:
                signal="Close" 
                 
    
    elif l_s == "Sell":
        if (df["High"]>= df["VWAP"] and 
            df["Volume"] > 1.5*df["roll_max_vol"]).shift(1) :
                signal="CLose_Buy"
        elif df["Close"]>df["Close"]+df["ATR"].shift(1):
                    signal="Close"
    return signal


def main():
    try:
        open_pos=obj.position()
        for ticker in tickers:
            long_short=""
            if len(open_pos)>0:
                open_pos_cur=open_pos[open_pos["currency"]==ticker]
                if open_pos_cur['isbuy'].tolist()[0]==True:
                    long_short="long"
                elif open_pos_cur['isbuy'].tolist()[0]==False:
                    long_short="short"
            data = obj.get_candles(currency,period='m5',number=250)
            ohlc=data.iloc[:,[0,1,2,3,8]]
            ohlc.columns=["open","close","high","low","volume"]
            signal=trade_signal(renko_merge(ohlc),long_short)
            
            
            if signal=="Buy":
                # con.open_trade(symbol=currency ,"...params")
                print("new long position initiated", currency)
            elif signal=="Sell":
                obj.open_trade('symbol',"...params")
                print("new short position initiated", currency)
            elif signal== "Close":
                obj.close_all_for_symbol(currency)
                print("All positions closed for: ",currency)
            elif signal=="CLose_Buy":
                obj.close_all_for_symbol(currency)
                print("Existing short positions closed for: ",currency)
                obj.open_trade('symbol',"...params")
                print("new long position initiated", currency)
            elif signal=="CLose_Sell":
                obj.close_all_for_symbol(currency)
                print("Existing long positions closed for: ",currency)
                obj.open_trade('symbol',"...params")
                print("new short position initiated", currency)
           
    except :
        print("error encountered..... skipping this iteration")



starttime = time.time()
timeout = time.time() + 60*60*1
while time.time() <= timeout :
    try : 
        print ("passthrough at ", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        main()
        time.sleep(300 - ((time.time()- starttime)%300.0))
    except KeyboardInterrupt():
        print ('\n\nkeyboard exception received. Exiting.')
        exit()
        

for currency in pairs:
    print("closing all positions for ", currency)
    obj.close_all_for_symbol(currency)
obj.close() 















