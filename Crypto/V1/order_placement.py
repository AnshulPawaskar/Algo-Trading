from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "./"))
path.append(base_dir)

from telegram import send
from config import PROJECT_NAME
em = f"\nProject: {PROJECT_NAME}\nFile: order_placement.py"

async def open(exchange, exchange_type, symbol, price, data):
    try:
        trade_type = data['Trade_Type']
        tp = data['Take_Profit']
        bal = data['Balance']
        avg_pct = data['Average_Percent']
        order_value = data['Order_Value']
        subs_order_value = data['Subsequent_Order_Value']
        subs_order_value_mul = data['Current_Subsequent_Order_Value_Multiplier']
        avg_pct_mul = data['Current_Average_Percent_Multiplier']
        qt = data['Quantity']
        processing = data['Processing']
        hold = data['Hold']
        if not processing:
            if prev_avg_price == 0 and bal > order_value and not hold:
                return True
            else:
                if price >= prev_avg_price*(1 + tp*0.01) and qt > 0 and hold:
                    return False
                elif price <= prev_avg_price*(1 - avg_pct*avg_pct_mul*0.01) and bal > subs_order_value*subs_order_value_mul and hold:
                    return True
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f"ERROR!{em}\nSymbol: {symbol}\nExchange: {exchange}\nType: {exchange_type}\nFunction: open\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}")
