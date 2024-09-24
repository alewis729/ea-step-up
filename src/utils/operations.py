import time
from typing import Optional
import math
from datetime import datetime
import os
from dotenv import load_dotenv
import MetaTrader5 as mt5

load_dotenv()


# Initializes and logs in
def initializeMT5():
    login = os.getenv("MT5_LOGIN")
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER")
    if not mt5.initialize():
        print("Initializing MT5 connection failed.")
        quit()
    print(f"> Connection to MT5 on server '{server}' was successful.")
    accInfo = mt5.account_info()
    if accInfo.login == login:
        return
    mt5.login(login, password, server)


# Calculates qty (Volume) based on account equity and a given risk
def getPositionSize(entry, sl, riskTolerance: float = 0.01):
    accountBalance = mt5.account_info().equity
    distanceToSL = abs(entry - sl)
    qty = riskTolerance * accountBalance / distanceToSL
    return math.floor(qty * 100) / 100


# Places a market or limit order
def createOrder(
    symbol,
    qty,
    isLong: Optional[bool] = None,
    entry: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    isLimit: Optional[bool] = False,
    comment: Optional[str] = "",
):
    isBullish = isLong if isLong is not None else entry > sl
    defaultComment = "Long entry" if isBullish else "Short entry"
    typeLimit = mt5.ORDER_TYPE_BUY_LIMIT if isBullish else mt5.ORDER_TYPE_SELL_LIMIT
    typeMarket = mt5.ORDER_TYPE_BUY if isBullish else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_PENDING if isLimit else mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": qty,
        "type": typeLimit if isLimit else typeMarket,
        # "deviation": 20,
        **({"price": float(entry)} if isLimit else {}),
        **({"sl": float(sl)} if sl is not None else {}),
        **({"tp": float(tp)} if tp is not None else {}),
        "magic": 729343,
        "comment": comment if comment != "" else defaultComment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    if result is None:
        print("Something went wrong when creating an order.")
        print(f"> request: {request}")
        print(mt5.last_error())
    return result


# Cancels all pending orders
def cancelAll(symbol: Optional["str"]):
    orders = mt5.orders_get(symbol=symbol) if symbol is not None else mt5.orders_get()
    if orders is None:
        print("No pending orders found")
        return
    print(orders)
    for order in orders:
        # only pending orders
        if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT]:
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order.ticket,
                "symbol": order.symbol,
                "magic": order.magic,
                "comment": "Canceling limit order",
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"> Limit order {order.ticket} canceled successfully.")
            else:
                print(
                    f"> Failed to cancel limit order {order.ticket}, retcode: {result.retcode}"
                )


# Cancels specific pending order based on position's comment
def cancelPendingOrder(id: str):
    orders = mt5.orders_get()
    if orders is None:
        print("No pending orders found")
        return
    order = next(
        (
            o
            for o in orders
            if o.comment == id
            and o.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT]
        ),
        None,
    )
    if order:
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": order.ticket,
            "symbol": order.symbol,
            "magic": order.magic,
            "comment": "Cancel order",
        }
        result = mt5.order_send(request)
        if result is None:
            print("Failed to cancel specific order. Error:", mt5.last_error())
        elif result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"> Order with comment '{id}' successfully canceled.")
        else:
            print(
                f"> Failed to cancel order with comment '{id}'. Retcode: {result.retcode}"
            )
            print(f"> order: {order}")
            print(f"> result: {result}")
    else:
        print(f"> No pending order with comment: '{id}'")
        print(f"> Current pending orders: {orders}")


# Updates SL and/or TP of an open position or pending order based on its comment
def updateSLTP(id: str, sl: float = None, tp: float = None):
    if sl is None and tp is None:
        print("Both SL and TP are null. Nothing to update.")
        return

    openPositions = mt5.positions_get()
    pendingOrders = mt5.orders_get()
    positions = []

    if openPositions is not None:
        positions.extend(openPositions)
    if pendingOrders is not None:
        positions.extend(pendingOrders)
    if openPositions is None:
        print("No active positions found.")
        return
    if not positions:
        print("No active positions or pending orders found. Nothing to update.")
        return

    trade = next((t for t in positions if t.comment == id), None)

    if trade:
        isOpen = hasattr(trade, "position_id") and trade.position_id != 0
        request = {
            "action": mt5.TRADE_ACTION_SLTP if isOpen else mt5.TRADE_ACTION_MODIFY,
            "symbol": trade.symbol,
            "magic": trade.magic,
            "comment": "Position update" if isOpen else "Order update",
            **({"position": trade.ticket} if isOpen else {"order": trade.ticket}),
            **({"price": trade.price_open} if not isOpen else {}),
            "sl": float(sl) if sl is not None else trade.sl,
            "tp": float(tp) if tp is not None else trade.tp,
        }
        result = mt5.order_send(request)
        if result is None:
            print("Order send failed. Error:", mt5.last_error())
        elif result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"> SL/TP for trade with comment '{id}' successfully updated.")
        else:
            print(f"> Failed to update SL/TP. Retcode: {result.retcode}")
            print(f"> trade: {trade}")
            print(f"> result: {result}")
    else:
        print(f"> No open position or pending order found with the comment: '{id}'")
        print(f"> Current positions: {positions}")


def testOperation():
    trades = [
        {"entry": 58000, "sl": 56000, "risk": 0.005, "comment": "p1"},
        {"entry": 55500, "sl": 54000, "risk": 0.01, "comment": "p2"},
        {"entry": 52000, "sl": 50000, "risk": 0.015, "comment": "p3"},
    ]

    # for t in trades:
    #     createOrder(
    #         symbol="BTCUSD",
    #         qty=getPositionSize(t["entry"], t["sl"], t["risk"]),
    #         entry=t["entry"],
    #         sl=t["sl"],
    #         isLimit=True,
    #         comment=t["comment"],
    #     )

    # cancelAll()
    # cancelPendingOrder("p2")
    updateSLTP("p1", 54000, 68000)

