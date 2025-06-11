from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "./"))
path.append(base_dir)

from websockets import connect
from argparse import ArgumentParser
from json import loads
from telegram import send
from config import PROJECT_NAME, MARKET_DATA_URL

em = f"\nProject: {PROJECT_NAME}\nFile: Price.py"
symbols = []

async def on_message(ws, message):
    try:
        data = loads(message)
        trade_price = None
        if ws.exchange == 'BINANCE':
            if 'e' in data.keys() and data['e'] in ['markPriceUpdate', 'trade']:
                trade_price = data['p']
                symbol = data['s']
        if trade_price is not None:
            print(symbol, trade_price)
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f"ERROR!{em}\nSymbol: {symbol}\nExchange: {ws.exchange}\nType: {ws.exchange_type}\nFunction: on_message\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}")

async def on_error(ws, error):
    await send(f"WEBSOCKET ERROR OCCURRED!{em}\nExchange: {ws.exchange}\nType: {ws.exchange_type}\nError: {error}")

async def on_close(ws, close_status_code, close_msg):
    await send(f"WEBSOCKET CLOSED!{em}\nExchange: {ws.exchange}\nExchange_Type: {ws.exchange_type}\nStatus Code: {close_status_code}\nMessage: {close_msg}")
    await create_websocket(ws.exchange, ws.exchange_type)

async def on_open(ws):
    try:
        await send(f"WEBSOCKET OPENED!\nExchange: {ws.exchange}\nExchange_Type: {ws.exchange_type}")
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f"ERROR!{em}\nExchange: {ws.exchange}\nType: {ws.exchange_type}\nFunction: on_open\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}")

async def create_websocket(exchange, exchange_type):
    try:
        stream_method = MARKET_DATA_URL[exchange][exchange_type]['METHOD']
        url = MARKET_DATA_URL[exchange][exchange_type['URL']]
        params = [f"{symbol['Symbol'].lower()}{stream_method}" for symbol in symbols]
        streams = '/'.join(params)
        url = f"{url}/{streams}"
        async with connect(url) as ws:
            ws.exchange = exchange
            ws.exchange_type = exchange_type
            ws.params = params
            await on_open(ws)
            try:
                async for message in ws:
                    await on_message(ws, message)
            except Exception as error:
                await on_error(ws, error)
            await on_close(ws, ws.close_code, ws.close_reason)
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f"ERROR!\n{em}\nExchange: {exchange}\nType: {exchange_type}\nFunction: create_websocket\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}")

async def main(exchange, exchange_type):
    try:
        await create_websocket(exchange, exchange_type)
    except KeyboardInterrupt:
        await send(f"PRICE FETCH HAS STOPPED!", False)
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f"ERROR!{em}\nFunction: main\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}")

if __name__ == "__main__":
    parser = ArgumentParser(description="Run the timeframe processing script.")
    parser.add_argument("--exchange", type=str, required=True, help="Exchange name (e.g., BINANCE, KUCOIN).")
    parser.add_argument("--exchange_type", type=str, required=True, help="Exchange type (e.g., SPOT, FUTURES).")
    
    args = parser.parse_args()
    main(args.exchange, args.exchange_type)

