import os
import MetaTrader5 as mt5
from utils.operations import (
    initializeMT5,
    createOrder,
    updateSLTP,
    cancelPendingOrder,
    cancelAll,
    closePosition,
    closeAllPositions,
)


def handleAlert(data):
    initializeMT5()
    print(f"> Received data: {data}")

    if data.get("licenseId") != os.getenv("LICENSE_ID"):
        print(f"> License '{data.get('licenseId')}' is invalid. Can not continue.")
        mt5.shutdown()
        return
    if data.get("command") is None:
        print(f"> Invalid command '{data.get('command')}'. Can not continue.")
        mt5.shutdown()
        return
    if data.get("symbol") is None:
        print(f"> Invalid symbol '{data.get('symbol')}'. Can not continue.")
        mt5.shutdown()
        return

    # create order / open position
    if data.get("command") in ["BUY", "SELL", "BUYLIMIT", "SELLLIMIT"]:
        order = createOrder(
            symbol=data.get("symbol"),
            risk=data.get("risk"),
            isLong=data.get("command") in ["BUY", "BUYLIMIT"],
            entry=data.get("price"),
            sl=data.get("sl"),
            tp=data.get("tp"),
            isLimit=data.get("command") in ["BUYLIMIT", "SELLLIMIT"],
            comment=data.get("comment"),
        )
        print(f"> Created order: {order}" )
    # update sl/tp
    elif data.get("command") in ["NEWSLTPLONG", "NEWSLTPSHORT"]:
        updateSLTP(data.get("comment"), data.get("sl"), data.get("tp"))
    # cancel pending order(s)
    elif data.get("command") in ["CANCELLONG", "CANCELSHORT"]:
        cancelPendingOrder(data.get('comment'))
    elif data.get("command") in ["CANCELALL"]:
        cancelAll(data.get('symbol'))
    # close open position(s)
    elif data.get("command") in ["CLOSELONG", "CLOSESHORT"]:
        closePosition(data.get("comment"), data.get("perc"))
    elif data.get("command") in ["CLOSEALL"]:
        closeAllPositions(data.get("symbol"))
