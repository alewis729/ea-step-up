from dotenv import load_dotenv
from utils.forceEncoding import forceEncoding
from utils.operations import initializeMT5, createOrder
from utils.getPositionSize import getPositionSize

load_dotenv()
forceEncoding()

testAccBalance = 100000
testCases = [
    {
        "symbol": "BTCUSD",
        "risk": 0.15,
        "price": 60000.05,
        "sl": 55123.45,
        "expected": 0.0307,
    },
    {
        "symbol": "XAUUSD",
        "risk": 0.15,
        "price": 2624.0000000,
        "sl": 2617,
        "expected": 0.21,
    },
    {
        "symbol": "EURUSD.i",
        "risk": 0.15,
        "price": 1.11,
        "sl": 1.10,
        "expected": 0.15,
    },
    {
        "symbol": "GBPJPY.i",
        "risk": 0.15,
        "price": 206.5,
        "sl": 210,
        "expected": 0.06097,
    },
    {
        "symbol": "CADCHF.i",
        "risk": 0.15,
        "price": 0.605,
        "sl": 0.6,
        "expected": 0.252537,
    },
    {
        "symbol": "SPX500",
        "risk": 0.15,
        "price": 5600,
        "sl": 5500,
        "expected": 0.15,
    },
    # {
    #     "symbol": "CADJPY.i",
    # },
    # {
    #     "symbol": "ETHUSD",
    # },
    # {
    #     "symbol": "NDX100",
    # },
    # {
    #     "symbol": "FRA40",
    # },
    # {
    #     "symbol": "XAGUSD",
    # },
]


def positionSizeTests():
    print(f"> Running positionSize tests.")
    for index, trade in enumerate(testCases):
        expected = round(float(trade.get("expected")), 2)
        volume = getPositionSize(
            symbol=trade.get("symbol"),
            entry=trade.get("price"),
            sl=trade.get("sl"),
            riskPercent=trade.get("risk"),
            accBalance=testAccBalance
        )
        if expected == volume:
            print(
                f"> ✅ Test {index}: Resulting volume for {trade.get("symbol")} is equal to expected volume."
            )
        else:
            print(
                f"> ❌ Test {index}: Resulting volume for {trade.get("symbol")} is incorrect. Expected: '{expected}'; Received: '{volume}'"
            )
            break

def createOrderTests():
    data = {
        "symbol": "BTCUSD",
        "risk": 0.15,
        "price": 60000.05,
        "sl": 55123.45,
        "tp": 70000.000005,
        "comment": "p7.2-BTC-9",
    }
    order = createOrder(
        symbol=data.get("symbol"),
        risk=data.get("risk"),
        isLong=True,
        entry=data.get("price"),
        sl=data.get("sl"),
        tp=data.get("tp"),
        isLimit=True,
        comment=data.get("comment"),
    )
    print(f"> ✅ Created order: {order}" )

def main():
    print("🐍 Python test script running...")
    print("---------- ---------- ---------- ---------- ----------")
    initializeMT5()
    positionSizeTests()
    # createOrderTests()


main()
