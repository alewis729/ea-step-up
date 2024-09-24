import websocket

ws_url = "ws://localhost:3000/websocket"

def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("WebSocket connection established")
    # time.sleep(5)
    # send_message_to_server(ws)

def send_message_to_server(ws):
    ws.send('{"action": "heartbeat", "message": "Client is still connected"}')

if __name__ == "__main__":
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # Assign the on_open callback separately
    ws.on_open = on_open
    ws.run_forever()
