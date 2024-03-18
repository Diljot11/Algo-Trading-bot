# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 04:59:34 2024

@author: singh
"""


from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from SmartApi import SmartConnect
import urllib
import json
import os
from pyotp import TOTP


key_path = r"D:\dsingh"
os.chdir(key_path)

key_secret = open("Angel One API.txt","r").read().split()

obj=SmartConnect(api_key=key_secret[0])
data = obj.generateSession(key_secret[2],key_secret[3],TOTP(key_secret[4]).now())
feed_token = obj.getfeedToken()



sws = SmartWebSocketV2(data["data"]["jwtToken"], key_secret[0], key_secret[2], feed_token)

instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = urllib.request.urlopen(instrument_url)
instrument_list = json.loads(response.read())

def token_lookup(ticker, instrument_list, exchange="NSE"):
    for instrument in instrument_list:
        if instrument["name"] == ticker and instrument["exch_seg"] == exchange and instrument["symbol"].split('-')[-1] == "EQ":
            return instrument["token"]
stock=token_lookup("ADANITENT", instrument_list)


correlation_id = "stream_1" #any string value which will help identify the specific streaming in case of concurrent streaming
action = 1 #1 subscribe, 0 unsubscribe
mode = 3 #1 for LTP, 2 for Quote and 2 for SnapQuote

token_list = [{"exchangeType": 1, "tokens": ["25"]}]


def on_data(wsapp, message):
    print("Ticks: {}".format(message))



        
        
def on_open(wsapp):
    print("on open")
    sws.subscribe(correlation_id, mode, token_list)


def on_error(wsapp, error):
    print(error)
    
def on_close(wsapp):
    print("Close")


# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error


sws.connect()