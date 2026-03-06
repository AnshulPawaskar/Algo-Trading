import websocket
import json
import requests
import threading
import time
from collections import deque

# -------------------
# CONFIG
# -------------------

SYMBOL = "BTCUSD"

WS_URL = "wss://socket.india.delta.exchange"
REST_URL = "https://api.india.delta.exchange/v2"

DELTA_WINDOW = 30        # seconds
WHALE_THRESHOLD = 50     # trade size considered whale

trade_window = deque()

buy_volume = 0
sell_volume = 0

open_interest = 0
funding_rate = 0
previous_oi = 0


# -------------------
# REST DATA
# -------------------

def get_open_interest():
    global open_interest
    try:
        r = requests.get(f"{REST_URL}/tickers/{SYMBOL}")
        data = r.json()
        open_interest = float(data["result"]["open_interest"])
    except:
        pass


def get_funding_rate():
    global funding_rate
    try:
        r = requests.get(f"{REST_URL}/tickers/{SYMBOL}")
        data = r.json()
        funding_rate = float(data["result"]["funding_rate"])
    except:
        pass


# -------------------
# DELTA CALCULATION
# -------------------

def calculate_delta():

    global buy_volume, sell_volume

    buy_volume = 0
    sell_volume = 0

    now = time.time()

    # keep only last 30 seconds
    while trade_window and now - trade_window[0]["time"] > DELTA_WINDOW:
        trade_window.popleft()

    for trade in trade_window:

        if trade["side"] == "buy":
            buy_volume += trade["size"]

        else:
            sell_volume += trade["size"]

    return buy_volume - sell_volume


# -------------------
# SIGNAL LOGIC
# -------------------

def generate_signal(delta, oi_change):

    if delta > 30 and oi_change > 0:
        return "BUY PRESSURE"

    if delta < -30 and oi_change > 0:
        return "SELL PRESSURE"

    if delta > 30 and oi_change < 0:
        return "SHORT SQUEEZE"

    if delta < -30 and oi_change < 0:
        return "LONG LIQUIDATION"

    return "NEUTRAL"


# -------------------
# WEBSOCKET HANDLER
# -------------------

def on_message(ws, message):

    global previous_oi

    data = json.loads(message)

    if data.get("type") != "all_trades":
        return

    size = float(data["size"])

    if data["buyer_role"] == "taker":
        side = "buy"
    elif data["seller_role"] == "taker":
        side = "sell"
    else:
        return

    # Whale detection
    if size >= WHALE_THRESHOLD:

        if side == "buy":
            print("🐋 WHALE BUY:", size)

        else:
            print("🐋 WHALE SELL:", size)

    trade_window.append({
        "time": time.time(),
        "side": side,
        "size": size
    })

    delta = calculate_delta()

    get_open_interest()

    oi_change = open_interest - previous_oi
    previous_oi = open_interest

    signal = generate_signal(delta, oi_change)

    # liquidity sweep detection
    if abs(delta) > 80:
        sweep = "LIQUIDITY SWEEP"
    else:
        sweep = ""

    print("\n--------------------------")
    print("Delta (30s):", round(delta,2))
    print("Buy Vol:", round(buy_volume,2))
    print("Sell Vol:", round(sell_volume,2))
    print("Open Interest:", open_interest)
    print("OI Change:", round(oi_change,2))
    print("Funding:", funding_rate)
    print("Signal:", signal, sweep)
    print("--------------------------")


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


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, a, b):
    print("Socket Closed")


# -------------------
# FUNDING LOOP
# -------------------

def funding_loop():

    while True:
        get_funding_rate()
        time.sleep(60)


# -------------------
# MAIN
# -------------------

if __name__ == "__main__":

    get_open_interest()
    get_funding_rate()

    threading.Thread(target=funding_loop, daemon=True).start()

    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()