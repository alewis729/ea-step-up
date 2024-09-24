import MetaTrader5 as mt5
from utils.operations import initializeMT5, testOperation

print("🏃‍♂️ Python script running...")
print("---------- ---------- ---------- ---------- ----------")
initializeMT5()
testOperation()

mt5.shutdown()
