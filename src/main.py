import os
from dotenv import load_dotenv
import websocket
import threading
import time
import json
from utils.handler import handleAlert
from utils.forceEncoding import forceEncoding

load_dotenv()
forceEncoding()

wsURL = os.getenv("WS_URL")

print("🐍 Python script running...")
print(f"> LICENSE_ID: {os.getenv("LICENSE_ID")}")
print(f"> WS_URL: {wsURL}")
print("---------- ---------- ---------- ---------- ----------")


def on_message(ws, message):
    data = json.loads(message)
    handleAlert(data)


def on_error(ws, error):
    print(f"> Error: {error}")


def on_close(ws, statusCode, closeMessage):
    print(
        f"> WebSocket connection closed with code {statusCode}. Reason: {closeMessage}"
    )


def on_open(ws):
    print("> WebSocket connection established.")


def keepAlive(ws):
    while True:
        ws.ping()
        time.sleep(30)


if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        wsURL, on_message=on_message, on_error=on_error, on_close=on_close
    )

    # Assign the on_open callback separately
    ws.on_open = on_open
    ws.run_forever()

    keepAliveThread = threading.Thread(target=keepAlive, args=(ws,))
    keepAliveThread.daemon = True
    keepAliveThread.start()
