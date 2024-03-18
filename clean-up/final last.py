# -*- coding: utf-8 -*-
"""
Created on Fri May 13 04:16:03 2022

@author: singh
"""


import datetime
from alpha_vantage.timeseries import TimeSeries
# import numpy as np
import pandas as pd
from smartapi import SmartConnect
# from smartapi import SmartWebSocket
# import statsmodels.api as sm 
import time
import copy
import requests
import json
import pyotp


obj=SmartConnect(api_key="3JsYBijP")
qr=("xxxx")
totp=pyotp.TOTP(qr)
totp=totp.now()
data = obj.generateSession("D104396","diljot2001")
print(data)
refreshToken= data['data']['refreshToken']

feedToken=obj.getfeedToken()

userProfile= obj.getProfile(refreshToken)

tickers=["ONGC","SBIN","BRITANNIA","COALINDIA","NTPC","SUNPHARMA","TATASTEEL","ADANIPORTS","M&M","HDFCLIFE","RELIANCE","BAJAJ-AUTO","HINDUNILVR","BPCL","LT","DRREDDY","ICICIBANK","KOTAKBANK","BHARTIARTL","CIPLA","SBILIFE","ASIANPAINT","TATACONSUM","MARUTI","HCLTECH","INDUSINDBK","TCS","TITAN"]



stocks = json.loads(requests.get('https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json').text)
for ticker in tickers:
    for info in stocks :
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
    df['H_PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L_PC'] = abs(df['Low'] - df['Close'])
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



def renko_merge(DF):
    df=copy.deepcopy(DF)
    
    
    # vwap=VWAP(df)
    
    df["date"]=df.index
    df["ATR"]= ATR(df,20)["ATR"]
    df["VWAP"]=VWAP(df)["Vwap"]
    df["SMA"]=SMA(df,200)
    df["EMA"]=EMA(df,50)
    df["roll_max_cp"]=df["High"].rolling(20).max()
    df["roll_min_cp"]= df["Low"].rolling(20).min()
    df["roll_max_vol"]= df["Volume"].rolling(20).max()
    df.dropna(inplace=True)

    return df






def trade_signal(merged_df,l_s):
    # function to generate signal 
    
    signal=""
    df=copy.deepcopy(merged_df)
    if l_s == "":
       
        # if df["Low"]<= df["VWAP"] and \
        #              df["Volume"]>1.5*df["roll_max_vol"].shift(1):
        #                  signal="Close_Sell"
        # elif df["Close"]< df["Close"]- df["ATR"]:
        #         signal="Close_the_buy"
        if (df["High"].tolist()[-1] >= df["VWAP"].tolist()[-1] and  
            df["Volume"].tolist()[-1] > 1.5*df["roll_max_vol"].tolist()[-2]) :
                signal="Buy"
        elif df["Low"].tolist()[-1]<= df["VWAP"].tolist()[-1] and \
              df["Volume"].tolist()[-1]>1.5*df["roll_max_vol"].tolist()[-1]:
                  signal="Sell"
                            
    elif l_s == "Buy":
        if df["Low"].tolist()[-1]<= df["VWAP"].tolist()[-1] and \
                     df["Volume"].tolist()[-1]>1.5*df["roll_max_vol"].tolist()[-2]:
                         signal="Close_Sell"
        elif df["Close"].tolist()[-1]< df["Close"].tolist()[-1]- df["ATR"].tolist()[-1]:
                signal="Close_the_buy" 
                 
    
    elif l_s == "Sell":
        if (df["High"].tolist()[-1]>= df["VWAP"].tolist()[-1] and 
            df["Volume"].tolist()[-1] > 1.5*df["roll_max_vol"].tolist()[-2]) :
                signal="CLose_Buy"
        elif df["Close"].tolist()[-1]>df["Close"].tolist()[-1]+df["ATR"].tolist()[-2]:
                    signal="Close_the_sell"
    return signal
# trade_signal(ohlc,"")

def main():
    # try:
        ticker_info={}
        for ticker in tickers:
            # open_pos=obj.position()
            for info in stocks :
                if info["exch_seg"] == "NSE":
                    if info["symbol"] == ticker +"-EQ":
                        ticker_info[ticker]=info
                        a=obj.ltpData(ticker_info[ticker]["exch_seg"], ticker_info[ticker]["symbol"], ticker_info[ticker]["token"])
                        # print(ticker +','+ ticker_info[ticker]["token"] )
            long_short=""
                        
            # position = obj.position()
            # pos=position["data"]

            # if len(pos)>0:
            #     open_pos=pos[pos["data"]==ticker]
            #     if open_pos['isbuy'].tolist()[0]==True:
            #         long_short="long"
            #     elif open_pos['isbuy'].tolist()[0]==False:
            #         long_short="short"
            try:
                times = str(time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time())))
                historicParam={
                    
                "exchange": "NSE",
                "symboltoken": ticker_info[ticker]["token"],
                "interval": "ONE_MINUTE",
                "fromdate": "2021-02-08 09:00", 
                "todate": times
                }
                # pd.DataFrame(type(obj.getCandleData(historicParam)))
                a=obj.ltpData(ticker_info[ticker]["exch_seg"], ticker_info[ticker]["symbol"], ticker_info[ticker]["token"])
                ohlc=pd.DataFrame(obj.getCandleData(historicParam)["data"])
                ohlc.columns=["Date","Open","High","Low","Close","Volume"]
                
                ohlc["Date"].append(datetime(time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))))
                ohlc["Open"].append(a["data"]["open"])
                ohlc["Low"].append(a["data"]["low"])
                ohlc["Close"].append(a["data"]["close"])
                ohlc["High"].append(a["data"]["high"])
                
            except Exception as e:
                print("Historic Api failed: {}".format(e))
            signal=trade_signal(renko_merge(ohlc),long_short)
            
            
            if signal=="Buy":
               try:
                   orderparams = {
                       "variety": "NORMAL",
                       "tradingsymbol": ticker_info[ticker]["symbol"],
                       "symboltoken": ticker_info[ticker]["token"],
                       "transactiontype": "BUY",
                       "exchange": "NSE",
                       "ordertype": "MARKET",
                       "producttype": "INTRADAY",
                       "duration": "DAY",
                       "price": "0",
                       "squareoff": "0",
                       "stoploss": "0",
                       "quantity": "1"
                       }
                   orderId=obj.placeOrder(orderparams)
                   print("new long position initiated "+ ticker_info[ticker]["name"] + "  The order id is: {}".format(orderId))
               except Exception as e:
                    print("Order placement failed: {}".format(e.message))
                   
            elif signal=="Sell":
                try:
                    orderparams = {
                        "variety": "NORMAL",
                        "tradingsymbol": ticker_info[ticker]["symbol"],
                        "symboltoken": ticker_info[ticker]["token"],
                        "transactiontype": "SELL",
                        "exchange": "NSE",
                        "ordertype": "MARKET",
                        "producttype": "INTRADAY",
                        "duration": "DAY",
                        "price": "0",
                        "squareoff": "0",
                        "stoploss": "0",
                        "quantity": "1"
                        }
                    orderId=obj.placeOrder(orderparams)
                    print("new short position initiated "," The order id is: {}".format(orderId))
                except Exception as e:
                     print("Order placement failed: {}".format(e.message))
                     
              
            elif signal== "Close_the_buy":
               try:
                   orderparams = {
                       "variety": "NORMAL",
                       "tradingsymbol": ticker_info[ticker]["symbol"],
                       "symboltoken": ticker_info[ticker]["token"],
                       "transactiontype": "SELL",
                       "exchange": "NSE",
                       "ordertype": "MARKET",
                       "producttype": "INTRADAY",
                       "duration": "DAY",
                       "price": "0",
                       "squareoff": "0",
                       "stoploss": "0",
                       "quantity": "1"
                       }
                   orderId=obj.placeOrder(orderparams)
                   print("buy positions closed "+ ticker +",The order id is: {}".format(orderId))
               except Exception as e:
                    print("Order placement failed: {}".format(e.message))
                    
               
            elif signal== "Close_the_sell":
               try:
                   orderparams = {
                       "variety": "NORMAL",
                       "tradingsymbol": ticker_info[ticker]["symbol"],
                       "symboltoken": ticker_info[ticker]["token"],
                       "transactiontype": "BUY",
                       "exchange": "NSE",
                       "ordertype": "MARKET",
                       "producttype": "INTRADAY",
                       "duration": "DAY",
                       "price": "0",
                       "squareoff": "0",
                       "stoploss": "0",
                       "quantity": "1"
                       }
                   orderId=obj.placeOrder(orderparams)
                   print("sell positions closed "+ ticker +",The order id is: {}".format(orderId))
               except Exception as e:
                    print("Order placement failed: {}".format(e.message))
                    
                
            elif signal=="CLose_Buy":
                try:
                    orderparams = {
                        "variety": "NORMAL",
                        "tradingsymbol": ticker_info[ticker]["symbol"],
                        "symboltoken": ticker_info[ticker]["token"],
                        "transactiontype": "BUY",
                        "exchange": "NSE",
                        "ordertype": "MARKET",
                        "producttype": "INTRADAY",
                        "duration": "DAY",
                        "price": "0",
                        "squareoff": "0",
                        "stoploss": "0",
                        "quantity": "1"
                        }
                    orderId=obj.placeOrder(orderparams)
                    print("sell positions closed "+ ticker +",The order id is: {}".format(orderId))
                except Exception as e:
                     print("Order placement failed: {}".format(e.message))
                     
                try:
                     orderparams = {
                         "variety": "NORMAL",
                         "tradingsymbol": ticker_info[ticker]["symbol"],
                         "symboltoken": ticker_info[ticker]["token"],
                         "transactiontype": "BUY",
                         "exchange": "NSE",
                         "ordertype": "MARKET",
                         "producttype": "INTRADAY",
                         "duration": "DAY",
                         "price": "0",
                         "squareoff": "0",
                         "stoploss": "0",
                         "quantity": "1"
                         }
                     orderId=obj.placeOrder(orderparams)
                     print("new long position initiated "," The order id is: {}".format(orderId))
                except Exception as e:
                      print("Order placement failed: {}".format(e.message))
                     
            elif signal=="CLose_Sell":
                try:
                    orderparams = {
                        "variety": "NORMAL",
                        "tradingsymbol": ticker_info[ticker]["symbol"],
                        "symboltoken": ticker_info[ticker]["token"],
                        "transactiontype": "SELL",
                        "exchange": "NSE",
                        "ordertype": "MARKET",
                        "producttype": "INTRADAY",
                        "duration": "DAY",
                        "price": "0",
                        "squareoff": "0",
                        "stoploss": "0",
                        "quantity": "1"
                        }
                    orderId=obj.placeOrder(orderparams)
                    print("long position closed "," The order id is: {}".format(orderId))
                except Exception as e:
                     print("Order placement failed: {}".format(e.message))
                    
                try:
                    orderparams = {
                        "variety": "NORMAL",
                        "tradingsymbol": ticker_info[ticker]["symbol"],
                        "symboltoken": ticker_info[ticker]["token"],
                        "transactiontype": "SELL",
                        "exchange": "NSE",
                        "ordertype": "MARKET",
                        "producttype": "INTRADAY",
                        "duration": "DAY",
                        "price": "0",
                        "squareoff": "0",
                        "stoploss": "0",
                        "quantity": "1"
                        }
                    orderId=obj.placeOrder(orderparams)
                    print("new short position initiated "," The order id is: {}".format(orderId))
                except Exception as e:
                     print("Order placement failed: {}".format(e.message))
                    
           
    # except :
    #     print("error encountered..... skipping this iteration: ")



starttime = time.time()
# obj.ltpData(ticker_info[ticker]["exch_seg"], ticker_info[ticker]["symbol"], ticker_info[ticker]["token"])
timeout = time.time() + 60*60*1
while time.time() <= timeout :
    try : 
        print ("passthrough at ", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        main()
        time.sleep(300 - ((time.time()- starttime)%300.0))
    except KeyboardInterrupt():
        print ('\n\nkeyboard exception received. Exiting.')
        exit()
        
        
def Close_all():        
    ticker_info={}
    for ticker in tickers:
        
        for info in stocks :
            if info["exch_seg"] == "NSE":
                if info["symbol"] == ticker +"-EQ":
                    ticker_info[ticker]=info
        position = obj.position()
        pos=position["data"]
        print("closing all positions for ", ticker)
        if len(pos)>0:
            open_pos=pos[pos["data"]==ticker]
            if open_pos['isbuy'].tolist()[0]==True:
                     
                orderparams = {
                            "variety": "NORMAL",
                            "tradingsymbol": ticker_info[ticker]["symbol"],
                            "symboltoken": ticker_info[ticker]["token"],
                            "transactiontype": "SELL",
                            "exchange": "NSE",
                            "ordertype": "MARKET",
                            "producttype": "INTRADAY",
                            "duration": "DAY",
                            "price": "0",
                            "squareoff": "0",
                            "stoploss": "0",
                            "quantity": "1"
                            }
                orderId=obj.placeOrder(orderparams)
                        
            elif open_pos['isbuy'].tolist()[0]==False:
                orderparams = {
                    "variety": "NORMAL",
                    "tradingsymbol": ticker_info[ticker]["symbol"],
                    "symboltoken": ticker_info[ticker]["token"],
                    "transactiontype": "BUY",
                    "exchange": "NSE",
                    "ordertype": "MARKET",
                    "producttype": "INTRADAY",
                    "duration": "DAY",
                    "price": "0",
                    "squareoff": "0",
                    "stoploss": "0",
                    "quantity": "1"
                    }
                orderId=obj.placeOrder(orderparams)
close=Close_all()
try:
    logout=obj.terminateSession('D104396')
    print("Logout Successfull")
except Exception as e:
    print("Logout failed: {}".format(e.message))













