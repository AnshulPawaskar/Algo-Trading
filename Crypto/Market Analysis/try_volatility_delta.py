import websocket
import json
import requests
import threading
import time
from collections import deque

# ---------------------------
# CONFIG
# ---------------------------

SYMBOL = "BTCUSD"

WS_URL = "wss://socket.india.delta.exchange"
REST_URL = "https://api.india.delta.exchange/v2"

trade_window = deque(maxlen=2000)

buy_volume = 0
sell_volume = 0

open_interest = 0
funding_rate = 0
previous_oi = 0


# ---------------------------
# REST FUNCTIONS
# ---------------------------

def get_open_interest():
    global open_interest

    try:
        url = f"{REST_URL}/tickers/{SYMBOL}"
        data = requests.get(url).json()

        open_interest = float(data["result"]["open_interest"])

    except:
        pass


def get_funding_rate():
    global funding_rate

    try:
        url = f"{REST_URL}/tickers/{SYMBOL}"
        data = requests.get(url).json()

        funding_rate = float(data["result"]["funding_rate"])

    except:
        pass


# ---------------------------
# DELTA CALCULATION
# ---------------------------

def calculate_delta():

    global buy_volume, sell_volume

    buy_volume = 0
    sell_volume = 0

    for trade in trade_window:

        qty = trade["qty"]

        if trade["side"] == "buy":
            buy_volume += qty

        elif trade["side"] == "sell":
            sell_volume += qty

    return buy_volume - sell_volume


# ---------------------------
# SIGNAL ENGINE
# ---------------------------

def generate_signal(delta, oi_change):

    if delta > 20 and oi_change > 0:
        return "BUY PRESSURE"

    if delta < -20 and oi_change > 0:
        return "SELL PRESSURE"

    if delta > 20 and oi_change < 0:
        return "SHORT SQUEEZE"

    if delta < -20 and oi_change < 0:
        return "LONG LIQUIDATION"

    return "NEUTRAL"


# ---------------------------
# WEBSOCKET HANDLER
# ---------------------------

def on_message(ws, message):

    global previous_oi

    data = json.loads(message)
    # print(data)

    if "trades" not in data:
        return

    for trade in data["trades"]:

        qty = float(trade["size"])
        if trade["buyer_role"] == "taker":
            side = "buy"
        elif trade["seller_role"] == "taker":
            side = "sell"
        else:
            side = "unknown"

        trade_window.append({
            "qty": qty,
            "side": side
        })

    delta = calculate_delta()

    get_open_interest()

    oi_change = open_interest - previous_oi
    previous_oi = open_interest

    signal = generate_signal(delta, oi_change)

    print("\n=========================")
    print("Delta:", round(delta,2))
    print("Buy Volume:", round(buy_volume,2))
    print("Sell Volume:", round(sell_volume,2))
    print("Open Interest:", round(open_interest,2))
    print("OI Change:", round(oi_change,2))
    print("Funding Rate:", funding_rate)
    print("Signal:", signal)
    print("=========================\n")


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("Socket Closed")


def on_open(ws):

    print("Connected to Delta Exchange")

    subscribe = {
        "type": "subscribe",
        "payload": {
            "channels": [
                {
                    "name": "all_trades",
                    "symbols": [SYMBOL]
                }
            ]
        }
    }

    ws.send(json.dumps(subscribe))


# ---------------------------
# FUNDING LOOP
# ---------------------------

def funding_loop():

    while True:
        get_funding_rate()
        time.sleep(60)


# ---------------------------
# MAIN
# ---------------------------

if __name__ == "__main__":

    get_open_interest()
    get_funding_rate()

    threading.Thread(target=funding_loop, daemon=True).start()

    ws = websocket.WebSocketApp(
        WS_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.on_open = on_open
    ws.run_forever()