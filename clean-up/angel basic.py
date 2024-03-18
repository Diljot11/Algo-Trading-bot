# -*- coding: utf-8 -*-
"""
Created on Sun May  8 01:25:18 2022

@author: singh
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May  7 22:58:02 2022

@author: singh
"""

# package import statement
import pandas as pd
from smartapi import SmartConnect
# from smartapi import WebSocket #or from smartapi.smartConnect import SmartConnect
#import smartapi.smartExceptions #(for smartExceptions)

#create object of call
obj=SmartConnect(api_key="EK01aqVz")
                #optional
                #access_token = "your access token",
                #refresh_token = "your refresh_token")

#login api call

data = obj.generateSession("D104396","diljot2001")
refreshToken= data['data']['refreshToken']

#fetch the feedtoken
feedToken=obj.getfeedToken()

#fetch User Profile
userProfile= obj.getProfile(refreshToken)


Tickers=["HEROMOTOCO","TECHM","POWERGRID","ITC","ONGC","SBIN","BRITANNIA","COALINDIA","NTPC","SUNPHARMA","TATASTEEL","ADANIPORTS","M&M","HDFCLIFE","RELIANCE","BAJAJ-AUTO","HINDUNILVR","BPCL","LT","DRREDDY","ICICIBANK","KOTAKBANK","BHARTIARTL","CIPLA","SBILIFE","ASIANPAINT","TATACONSUM","MARUTI","HCLTECH","INDUSINDBK","TCS","TITAN"]
data={}


def VWAP(DF):
    df=DF.copy()
    df['TP'] = abs(df['High'] + df['Low'] + df['Close'])/3
    df['TPV'] = df['TP']*df['Volume']
    df['CPV'] = df['TPV'].shift(1)+ df['TPV'] #cpv=cummulative price*volume
    df['CV'] = df['Volume'] + df['Volume'].shift(1) #cv=cummulative volume
    df['Vwap'] = (df['CPV'])/(df['CV'])
    return df


#place order
try:
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "19500",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
        }
    orderId=obj.placeOrder(orderparams)
    print("The order id is: {}".format(orderId))
except Exception as e:
     print("Order placement failed: {}".format(e.message))
     
     
  
#Historic api
try:
    historicParam={
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "ONE_MINUTE",
    "fromdate": "2021-02-08 09:00", 
    "todate": "2022-05-08 09:16"
    }
    # pd.DataFrame(type(obj.getCandleData(historicParam)))
    
    historical_data=pd.DataFrame(obj.getCandleData(historicParam)["data"])
    historical_data.columns=["Date","Open","High","Low","Close","Volume"]
except Exception as e:
    print("Historic Api failed: {}".format(e))
#logout
try:
    logout=obj.terminateSession('Your Client Id')
    print("Logout Successfull")
except Exception as e:
    print("Logout failed: {}".format(e.message))