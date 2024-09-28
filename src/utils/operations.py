import os
from typing import Optional
import MetaTrader5 as mt5
from utils.getPositionSize import getPositionSize


# Initializes and logs in
def initializeMT5():
    login = os.getenv("MT5_LOGIN")
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER")
    if not mt5.initialize():
        print("> Initializing MT5 connection failed.")
        quit()
    print(f"> Connection to MT5 on server '{server}' was successful.")
    accInfo = mt5.account_info()
    if accInfo.login == login:
        print(f"> Already logged-in to account '{login}'.")
        return
    mt5.login(login, password, server)


# Places a market or limit order
def createOrder(
    symbol: str,
    qty: Optional[float] = None,
    risk: Optional[float] = None,
    isLong: Optional[bool] = None,
    entry: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    isLimit: Optional[bool] = False,
    comment: Optional[str] = None,
):
    if isLong is None and entry is None:
        print(
            "> Missing necessary values. Either pass `isLong` or `entry` to calculate direction."
        )
        return
    isBullish = isLong if isLong is not None else entry > sl
    defaultComment = "Long entry" if isBullish else "Short entry"
    orderTypeLimit = (
        mt5.ORDER_TYPE_BUY_LIMIT if isBullish else mt5.ORDER_TYPE_SELL_LIMIT
    )
    orderTypeMarket = mt5.ORDER_TYPE_BUY if isBullish else mt5.ORDER_TYPE_SELL
    finalQty = qty
    if (
        risk is not None
        and (float(risk) > 0.0 and float(risk) < 100.0)
        and sl is not None
    ):
        localEntryPrice = entry
        if entry is None:
            localEntryPrice = (
                mt5.symbol_info_tick(symbol).ask
                if isBullish
                else mt5.symbol_info_tick(symbol).bid
            )
        finalQty = getPositionSize(symbol, localEntryPrice, sl, risk)
    request = {
        "action": mt5.TRADE_ACTION_PENDING if isLimit else mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": finalQty,
        "type": orderTypeLimit if isLimit else orderTypeMarket,
        "deviation": 20,
        **({"price": float(entry)} if isLimit else {}),
        **({"sl": float(sl)} if sl is not None else {}),
        **({"tp": float(tp)} if tp is not None else {}),
        "magic": 729343,
        "comment": comment if comment is not None else defaultComment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    print(f"> request: {request}")
    result = mt5.order_send(request)
    if result is None:
        print("> Something went wrong when creating an order.")
        print(f"> request: {request}")
        print(mt5.last_error())
    return result


# Cancels all pending orders
def cancelAll(symbol: Optional[str] = None):
    orders = mt5.orders_get(symbol=symbol) if symbol is not None else mt5.orders_get()
    if orders is None:
        print("> No pending orders found.")
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
                "comment": "Cancel all orders",
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(
                    f"> Successfully canceled limit order {order.ticket} with comment '{order.comment}'."
                )
            else:
                print(
                    f"> Failed to cancel limit order {order.ticket}, retcode: {result.retcode}"
                )


# Cancels specific pending order based on position's comment
def cancelPendingOrder(id: str):
    orders = mt5.orders_get()
    if orders is None:
        print("> No pending orders found.")
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
            print("> Failed to cancel specific order. Error:", mt5.last_error())
        elif result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"> Successfully canceled order with comment '{id}'.")
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
        print("> Both SL and TP are null. Nothing to update.")
        return

    openPositions = mt5.positions_get()
    pendingOrders = mt5.orders_get()
    positions = []

    if openPositions is not None:
        positions.extend(openPositions)
    if pendingOrders is not None:
        positions.extend(pendingOrders)
    if openPositions is None:
        print("> No active positions found.")
        return
    if not positions:
        print("> No active positions or pending orders found. Nothing to update.")
        return

    trade = next((t for t in positions if t.comment == id), None)
    if trade:
        isOpen = hasattr(trade, "position_id") and trade.position_id != 0
        request = {
            "action": mt5.TRADE_ACTION_SLTP if isOpen else mt5.TRADE_ACTION_MODIFY,
            "symbol": trade.symbol,
            "magic": trade.magic,
            "comment": trade.comment,
            **({"position": trade.ticket} if isOpen else {"order": trade.ticket}),
            **({"price": trade.price_open} if not isOpen else {}),
            "sl": float(sl) if sl is not None else trade.sl,
            "tp": float(tp) if tp is not None else trade.tp,
        }
        result = mt5.order_send(request)
        if result is None:
            print("> Order send failed. Error:", mt5.last_error())
        elif result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"> Successfully updated SL/TP for trade with comment '{id}'.")
        else:
            print(f"> Failed to update SL/TP. Retcode: {result.retcode}")
            print(f"> trade: {trade}")
            print(f"> result: {result}")
    else:
        print(f"> No open position or pending order found with the comment: '{id}'")
        print(f"> Current open positions: {positions}")


# Closes an open position based on its comment, optionally closes % of the position
def closePosition(id: str, percent: Optional[float] = None):
    positions = mt5.positions_get()
    perc = 100.0
    if positions is None:
        print("> No active positions found.")
        return
    if percent is not None:
        if float(percent) <= 0.0 or float(percent) > 100.0:
            print(
                f"> Percent passed '{percent}' is invalid. Acceptable values are between 0 and 100."
            )
            return
        perc = float(percent)

    position = next((p for p in positions if p.comment == id), None)
    if position:
        volumeToClose = round(position.volume * perc / 100, 2)
        if volumeToClose < mt5.symbol_info(position.symbol).volume_min:
            print(
                f"> Volume to close '{volumeToClose}' is less than the broker's minimum lot size."
            )
            return

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": volumeToClose,
            "type": (
                mt5.ORDER_TYPE_SELL
                if position.type == mt5.POSITION_TYPE_BUY
                else mt5.ORDER_TYPE_BUY
            ),
            "position": position.ticket,
            "price": (
                mt5.symbol_info_tick(position.symbol).bid
                if position.type == mt5.POSITION_TYPE_BUY
                else mt5.symbol_info_tick(position.symbol).ask
            ),
            "deviation": 20,
            "magic": position.magic,
            "comment": position.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result is None:
            print("> Order send failed. Error:", mt5.last_error())
        elif result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"> Successfully closed {perc}% of the position with comment '{id}'.")
        else:
            print(f"> Failed to close position. Retcode: {result.retcode}")
            print(f"> position: {position}")
            print(f"> result: {result}")
    else:
        print(f"> No open position found with the comment: '{id}'")
        print(f"> Current open positions: {positions}")


# Closes all open positions
def closeAllPositions(symbol: Optional[str] = None):
    positions = (
        mt5.positions_get(symbol=symbol) if symbol is not None else mt5.positions_get()
    )
    if positions is None or len(positions) == 0:
        print("> No active positions found to close.")
        return

    for pos in positions:
        isLong = pos.type == mt5.POSITION_TYPE_BUY
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": (mt5.ORDER_TYPE_SELL if isLong else mt5.ORDER_TYPE_BUY),
            "position": pos.ticket,
            "price": (
                mt5.symbol_info_tick(pos.symbol).bid
                if isLong
                else mt5.symbol_info_tick(pos.symbol).ask
            ),
            "deviation": 20,
            "magic": pos.magic,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)

        if result is None:
            print(
                f"> Failed to close position '{pos.ticket}'. Error:", mt5.last_error()
            )
        elif result.retcode == mt5.TRADE_RETCODE_DONE:
            print(
                f"> Successfully closed position '{pos.ticket}' with comment '{pos.comment}' for symbol '{pos.symbol}'."
            )
        else:
            print(f"> Failed to close position {pos.ticket}. Retcode: {result.retcode}")
            print(f"> position: {pos}")
            print(f"> result: {result}")
