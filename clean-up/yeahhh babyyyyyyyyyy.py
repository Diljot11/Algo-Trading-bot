# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 16:56:00 2022

@author: singh
"""

import SmartApi
from SmartApi import SmartConnect
import pyotp

obj=SmartConnect(api_key="YH7jX695")

qr=("KWMUDEMPMYEYWNUCPFMW7P2IHA")
totp=pyotp.TOTP(qr)
totp=totp.now()
# totp=totp.generate_otp(0)

data = obj.generateSession("D104396","2001",totp)
print(data)
AUTH_TOKEN = data["data"]["jwtToken"] 
API_KEY = '6OnOXS91'

from SmartApi import SmartWebSocket

# feed_token=092017047
FEED_TOKEN=obj.feed_token
CLIENT_CODE="D104396"
token="mcx_fo|224395"
# token="nse_cm|2885&nse_cm|1594&nse_cm|11536&nse_cm|3045"
# token="mcx_fo|226745&mcx_fo|220822&mcx_fo|227182&mcx_fo|221599"
task="mw"
ss = SmartWebSocket(FEED_TOKEN, CLIENT_CODE)
# tick={}
# vol=[]
# ltp=[]
# high=0
# def on_message(ws, message):
#     global high
#     tick=message
#     a=tick[0]
#     print(a)
#     vol.append(a['v'])
#     ltp.append(a['ltp'])
    
#     if a['ltp']>high:
#         high=a['ltp']
#     print(high)
#     # print (tick)
    
# def on_open(ws):
#     print("on open")
#     ss.subscribe(task,token)
    
# def on_error(ws, error):
#     print(error)
    
# def on_close(ws):
#     print("Close")

# # Assign the callbacks.

# ss._on_open = on_open
# ss._on_message = on_message
# # print(res)

# ss._on_error = on_error
# ss._on_close = on_close

# ss.connect()

def on_message(ws, message):
    print(ss)
    print("Ticks: {}".format(message))
    
def on_open(ws):
    print("on open")
    ss.subscribe("mw",token)
    
def on_error(ws, error):
    print(error)
    
def on_close(ws):
    print("Close")

# Assign the callbacks.
ss._on_open = on_open
ss._on_message = on_message
ss._on_error = on_error
ss._on_close = on_close

ss.connect()
