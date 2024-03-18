# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 02:08:33 2023

@author: singh
"""


import json
import requests
import websocket


api_key = "3JsYBijP"
api_secret = "YOUR_API_SECRET"
client_code = "D104396"
username = "D104396"
password = "diljot2001"

# Authenticate and obtain access and refresh tokens
auth_url = "https://smartapi.angelbroking.com/publisher/user/v1/login"
auth_payload = {
    "clientcode": client_code,
    "password": password,
    "appid": api_key,
    "usernametype": "CUSTOMER",
    "source": "WEBAPI",
}
headers = {"Content-Type": "application/json"}
response = requests.post(auth_url, data=json.dumps(auth_payload), headers=headers)
print(response.text)
auth_data = json.loads(response.text)
access_token = auth_data["data"]["accessToken"]
refresh_token = auth_data["data"]["refreshToken"]


def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        ws.send(json.dumps({"a": "subscribe", "v": ["mw"]}))

    thread.start_new_thread(run, ())

ws_url = "wss://omnefeeds.angelbroking.com/NestHtml5Mobile/socket/stream"
ws = websocket.WebSocketApp(
    ws_url,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    header={
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
    },
)
ws.on_open = on_open
ws.run_forever()
