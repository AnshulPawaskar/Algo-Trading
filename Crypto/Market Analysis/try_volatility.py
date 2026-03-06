import websocket
import json
import requests
import threading
import time
from collections import deque

SYMBOL = "btcusdt"

BASE_REST = "https://fapi.binance.com"

# store last trades for delta calculation
trade_window = deque(maxlen=2000)

buy_volume = 0
sell_volume = 0

open_interest = 0
funding_rate = 0


# -----------------------------
# REST DATA
# -----------------------------

def get_open_interest():
    global open_interest

    url = f"{BASE_REST}/fapi/v1/openInterest"
    params = {"symbol": SYMBOL.upper()}

    try:
        data = requests.get(url, params=params).json()
        open_interest = float(data["openInterest"])
    except:
        pass


def get_funding_rate():
    global funding_rate

    url = f"{BASE_REST}/fapi/v1/premiumIndex"
    params = {"symbol": SYMBOL.upper()}

    try:
        data = requests.get(url, params=params).json()
        funding_rate = float(data["lastFundingRate"])
    except:
        pass


# -----------------------------
# DELTA CALCULATION
# -----------------------------

def calculate_delta():
    global buy_volume, sell_volume

    buy_volume = 0
    sell_volume = 0

    for trade in trade_window:

        qty = trade["qty"]
        is_sell = trade["is_sell"]

        if is_sell:
            sell_volume += qty
        else:
            buy_volume += qty

    return buy_volume - sell_volume


# -----------------------------
# SIGNAL LOGIC
# -----------------------------

def generate_signal(delta, oi_change):

    if delta > 30 and oi_change > 0:
        return "BUY PRESSURE"

    elif delta < -30 and oi_change > 0:
        return "SELL PRESSURE"

    elif delta > 30 and oi_change < 0:
        return "SHORT SQUEEZE"

    elif delta < -30 and oi_change < 0:
        return "LONG LIQUIDATION"

    return "NEUTRAL"


# -----------------------------
# WEBSOCKET HANDLER
# -----------------------------

previous_oi = 0


def on_message(ws, message):

    global previous_oi

    data = json.loads(message)
    print(data)

    qty = float(data["q"])
    is_sell = data["m"]

    trade_window.append({
        "qty": qty,
        "is_sell": is_sell
    })

    delta = calculate_delta()

    get_open_interest()

    oi_change = open_interest - previous_oi
    previous_oi = open_interest

    signal = generate_signal(delta, oi_change)

    print("\n==============================")
    print("Delta:", round(delta, 2))
    print("Buy Volume:", round(buy_volume, 2))
    print("Sell Volume:", round(sell_volume, 2))
    print("Open Interest:", round(open_interest, 2))
    print("OI Change:", round(oi_change, 2))
    print("Funding Rate:", funding_rate)
    print("Signal:", signal)
    print("==============================\n")


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")


def on_open(ws):
    print("WebSocket Connected")


# -----------------------------
# BACKGROUND FUNDING FETCHER
# -----------------------------

def funding_loop():

    while True:
        get_funding_rate()
        time.sleep(60)


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    get_open_interest()
    get_funding_rate()

    threading.Thread(target=funding_loop, daemon=True).start()

    socket = f"wss://fstream.binance.com/ws/{SYMBOL}@aggTrade"

    ws = websocket.WebSocketApp(
        socket,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.on_open = on_open

    ws.run_forever()