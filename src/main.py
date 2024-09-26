import os
from dotenv import load_dotenv
import websocket
import json
from utils.handler import handleAlert


load_dotenv()

print("🐍 Python script running...")
print("---------- ---------- ---------- ---------- ----------")


def on_message(ws, message):
    data = json.loads(message)
    handleAlert(data)


def on_error(ws, error):
    print(f"> Error: {error}")


def on_close(ws):
    print("> WebSocket connection closed.")


def on_open(ws):
    print("> WebSocket connection established.")


if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        os.getenv("WS_URL"), on_message=on_message, on_error=on_error, on_close=on_close
    )

    # Assign the on_open callback separately
    ws.on_open = on_open
    ws.run_forever()
