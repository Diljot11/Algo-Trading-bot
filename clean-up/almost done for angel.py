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



ticks = json.loads(requests.get('https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json').text)
for ticker in tickers:
    for info in ticks :
        if info["exch_seg"] == "NSE":
            if info["symbol"] == ticker +"-EQ":
                print (info["name"], info["symbol"])




pos_size=10


def ATR(DF,n):
    df=DF.copy()
    
    df['H_L'] = abs(df['High'] - df['Low'])
    df['H_PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L_PC'] = abs(df['Low'] - df['Close'])
    df['TR'] = df[['H_L','H_PC','L_PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df2=df.drop(['H_L','H_PC','L_PC'],axis=1)
    return df2

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
    
    
    # vwap=VWAP(df)
    
    df["date"]=df.index
    df["ATR"]= ATR(df,20)["ATR"]
    df["VWAP"]=VWAP(df)["Vwap"]
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
    try:
        ticker_info={}
        for ticker in tickers:
            # open_pos=obj.position()
            for info in ticks :
                if info["exch_seg"] == "NSE":
                    if info["symbol"] == ticker +"-EQ":
                        ticker_info[ticker]=info
                       
                        # print(ticker +','+ ticker_info[ticker]["token"] )
            long_short=""
                        
            position = obj.position()
            pos=position["data"]

            if len(pos)>0:
                open_pos=pos[pos["data"]==ticker]
                if open_pos['isbuy'].tolist()[0]==True:
                    long_short="Buy"
                elif open_pos['isbuy'].tolist()[0]==False:
                    long_short="Sell"
            try:
                   
                historicParam={
                    
                "exchange": "NSE",
                "symboltoken":"3045", #ticker_info[ticker]["token"],
                "interval": "ONE_MINUTE",
                "fromdate": "2021-02-08 09:00", 
                "todate": "2022-05-13 04:00"
                }
                # pd.DataFrame(type(obj.getCandleData(historicParam)))
                
                ohlc=pd.DataFrame(obj.getCandleData(historicParam)["data"])
                ohlc.columns=["Date","Open","High","Low","Close","Volume"]
                
             
               
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
                    
           
    except :
        print("error encountered..... skipping this iteration: ")



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
        
        
        
ticker_info={}
for ticker in tickers:
    
    for info in ticks :
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
   
try:
    logout=obj.terminateSession('Your Client Id')
    print("Logout Successfull")
except Exception as e:
    print("Logout failed: {}".format(e.message)) 
