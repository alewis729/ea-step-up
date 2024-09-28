import MetaTrader5 as mt5
from typing import Optional


# getDecimalCount(0.0001) => 4
# getDecimalCount(1e-05) => 5
def getDecimalCount(number):
    numberStr = f"{number:.10f}"
    decimalCount = len(numberStr.split(".")[1]) if "." in numberStr else 0
    return decimalCount


# Calculates qty (Volume) based on account equity and a given risk (%)
# riskPercent should be from 0 to 100. Example: 1.245 means 1.245% of the equity
def getPositionSize(
    symbol: str,
    entry,
    sl,
    riskPercent: float = 1.0,
    accBalance: Optional[float] = None,
):
    symInfo = mt5.symbol_info(symbol)
    if symInfo is None:
        print(f"> Symbol {symbol} not found.")
        return None
    if not symInfo.visible:
        mt5.symbol_select(symbol, True)

    if float(riskPercent) < 0 or float(riskPercent) > 100:
        print(f"> Risk amount of '{riskPercent}%' is invalid. (Use 0-100)")
        return 0.0

    tickSize = symInfo.trade_tick_size
    tickValue = symInfo.trade_tick_value
    volumeStep = symInfo.volume_step
    roundPoint = getDecimalCount(symInfo.point) + 1

    if tickSize == 0 or tickValue == 0 or volumeStep == 0:
        print(f"> symInfo: {symInfo}")
        print(
            f"> 🧮 getPositionSize(): Volume cannot be calculated; tickSize: {tickSize}, tickValue: {tickValue}, volumeStep: {volumeStep}"
        )
        return None

    accountBalance = accBalance if accBalance is not None else mt5.account_info().equity
    riskAmount = accountBalance * (riskPercent / 100)
    distanceToSL = round(abs(entry - sl), roundPoint)
    volumeStepAmount = (distanceToSL / tickSize) * tickValue * volumeStep

    if volumeStepAmount == 0:
        print(f"> symInfo: {symInfo}")
        print(
            f"> 🧮 getPositionSize(): Volume cannot be calculated; distanceToSL: {distanceToSL}, roundPoint: {roundPoint}, volumeStepAmount: {volumeStepAmount}, tickSize: {tickSize}, tickValue: {tickValue}, volumeStep: {volumeStep}"
        )
        return None

    qty = riskAmount / volumeStepAmount * volumeStep
    volume = round(qty, 2)
    print(
        f"> 🧮 getPositionSize(): accountBalance: {accountBalance}, riskAmount: {riskAmount}, distanceToSL: {distanceToSL}, volumeStepAmount: {volumeStepAmount}, qty: {qty}"
    )
    print(
        f"> 🧮 Calculated volume: '{volume}' for symbol: {symbol} with entry: {entry}, sl: {sl}, and riskPercent: {riskPercent}%"
    )
    return volume
