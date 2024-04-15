from polygon import RESTClient
import pandas as pd
from datetime import datetime
import MetaTrader5 as mt5
import pytz
import time
import csv



login = 'Your info'
server = 'Your info'
password = 'Your info'
email = 'Your info'
symbol = 'US500Cash'

def get_polygon_data(symbol):
    # Initialize the REST client with your Polygon API key
    client = RESTClient(api_key="Your API KEY")

    # Get the current date in the "YYYY-MM-DD" format
    current_date = datetime.now().strftime("%Y-%m-%d")

    # List Aggregates (Bars) from Polygon
    aggs = []
    for a in client.list_aggs(ticker=symbol, multiplier=5, timespan="minute", from_=current_date, to=current_date, limit=50000):
        aggs.append(a)


    # Create a DataFrame out of the obtained data
    aggs_frame = pd.DataFrame(aggs)
    # Convert the timestamp in milliseconds into the datetime format
    aggs_frame['timestamp'] = pd.to_datetime(aggs_frame['timestamp'], unit='ms')

    # Display data
    print("\nDisplay DataFrame with Polygon data")
    print(aggs_frame)
    return aggs_frame

# Example usage:
polygon_symbol = "I:SPX"




def get_account_info(login, server, password):
    # display data on the MetaTrader 5 package
    print("MetaTrader5 package author: ", mt5.__author__)
    print("MetaTrader5 package version: ", mt5.__version__)

    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()

    # connect to the trade account specifying a password and a server
    authorized = mt5.login(login=login, server=server, password=password)
    if authorized:
        account_info = mt5.account_info()
        if account_info != None:
            # display trading account data 'as is'
            print(account_info)
            # display trading account data in the form of a dictionary
            print("Show account_info()._asdict():")
            account_info_dict = mt5.account_info()._asdict()
            for prop in account_info_dict:
                print("  {}={}".format(prop, account_info_dict[prop]))
            print()

            # convert the dictionary into DataFrame and print
            df = pd.DataFrame(list(account_info_dict.items()), columns=['property', 'value'])
            print("account_info() as dataframe:")
            print(df)
    else:
        print("failed to connect to trade account, error code =", mt5.last_error())

    # shut down connection to the MetaTrader 5 terminal
    mt5.shutdown()


def get_stock_info(symbol):
    # display data on the MetaTrader 5 package
    print("MetaTrader5 package author: ", mt5.__author__)
    print("MetaTrader5 package version: ", mt5.__version__)

    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize(login=login, server=server, password=password):
        print("initialize() failed, error code =", mt5.last_error())
        quit()

        # attempt to enable the display of the EURJPY symbol in MarketWatch
    selected = mt5.symbol_select(symbol, True)
    if not selected:
        print(f"Failed to select {symbol}")
        mt5.shutdown()
        quit()

        # display symbol properties
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info != None:
        # display the terminal data 'as is'
        current_price = float(symbol_info.bid)
        print(f"The current price of {symbol} is: $", current_price)
        print(symbol_info)
        print(f"{symbol}: spread =", symbol_info.spread, "  digits =", symbol_info.digits)
        # display symbol properties as a list
        print("Show symbol_info(\"US500Cash\")._asdict():")
    symbol_info_dict = mt5.symbol_info(symbol)._asdict()
    for prop in symbol_info_dict:
        print("  {}={}".format(prop, symbol_info_dict[prop]))

    # shut down connection to the MetaTrader 5 terminal
    mt5.shutdown()

    return current_price, symbol_info_dict

def analyze_and_setup_trades_metatrader(data, account_size=50000, max_loss_percent=1.0, confidence_threshold=0.4):
    # Your Trading Strategy Logic
    #Analyze the recent data and set up the variables you need to execute a trade
    return data




def execute_trade_xm(symbol='US500Cash', entry_price=float, stop_loss=float, take_profit=float, risk=100000, direction='buy'):
    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize(login=login, server=server, password=password):
        print("initialize() failed, error code =", mt5.last_error())
        quit()

    # prepare the buy request structure
    symbol = symbol
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        quit()

    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select({}}) failed, exit", symbol)
            mt5.shutdown()
            quit()

    total_lot = round(0.01 * (risk / (abs(entry_price - stop_loss))), 1)
    max_lot_per_trade = 800.0

    # Loop to send trades in chunks if total_lot exceeds 800
    while total_lot > 0:
        lot = min(total_lot, max_lot_per_trade)  # Ensure we don't exceed total_lot
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        pending_order_price = float(entry_price)
        stop_loss = round(stop_loss, symbol_info.digits)
        take_profit = round(take_profit, symbol_info.digits)
        deviation = 10
        if direction == 'buy':
            if price > pending_order_price:
                type = mt5.ORDER_TYPE_BUY_LIMIT
            else:
                type = mt5.ORDER_TYPE_BUY_STOP
        else:
            if price < pending_order_price:
                type = mt5.ORDER_TYPE_SELL_LIMIT
            else:
                type = mt5.ORDER_TYPE_SELL_STOP
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": pending_order_price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": deviation,
            "comment": "V1",
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        print(f'Stop loss is: ${stop_loss} & take profit is: ${take_profit} & volume is: {lot}')
        # send a trading request
        result = mt5.order_send(request)
        print("Order Send Result:", result)  # Add this line to check the result

        if result is None:
            print("Order send failed. Result is None.")
            print("Last error:", mt5.last_error())
            quit()

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Order send failed. Retcode={}".format(result.retcode))
            print("Last error:", mt5.last_error())
            # Your additional error handling logic
            quit()

        # Deduct the sent lot from total_lot
        total_lot -= lot

        print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol, lot, price, deviation));
        if result is not None and result.retcode != mt5.TRADE_RETCODE_DONE:
            print("2. order_send failed, retcode={}".format(result.retcode))
            # request the result as a dictionary and display it element by element
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field, result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
            print("shutdown() and quit")
            mt5.shutdown()
            quit()

        print("2. order_send done, ", result)
        if result is not None and result.retcode != mt5.TRADE_RETCODE_DONE:
            print("   opened position with POSITION_TICKET={}".format(result.order))

    mt5.shutdown()  # Shutdown connection after all trades are sent
    return result





get_stock_info(symbol)
data = get_polygon_data(polygon_symbol)
trade_data = analyze_and_setup_trades_metatrader(data, account_size=100000)

execute_trade_xm(entry_price=trade_data['entry_price'],take_profit=trade_data['take_profit'],direction=trade_data['bias'],stop_loss=trade_data['stop_loss'])

