# EA

This is a python project that connects to a websocket server and expects messages that would originally come from TradingView alerts. Those messages are processed to some extent on the server and when this project receives them are further processed in python and used to open and manage trades via MT5.

### Install and setup locally

```bash
git clone
python -m venv venv
source venv/Scripts/activate # activates venv on Windows
# source venv/bin/activate # activates venv on macOS/linux
pip3 install -r requirements.txt
```

### Test locally

- Go through the installation process from above
- You need the webhook/websocket server to be running, either locally or to be publicly accessible.
- Update the url passed to `WebSocketApp` (`ws_url`) to point to the websocket server.
- Run the script with `python3 src/webhook_client.py`
- Simulate sending an alert to the webhook server (via curl on macOS for example, with: `curl -X POST http://localhost:3000/webhook -H 'Content-Type: application/json; charset=utf-8' -d '{"text": "BTCUSD Greater Than 9000"}'`)
- The webhook server should receive the alert, and should communicate the necessary information to python. You should be able to see the information on the console that runs python.

### Important notes

This project is meant to be ran on Windows OS. It might be possible to run this on macOS or linux but MT5 is meant for Windows and crashes frequently on macOS. Additionally, it seems like the [MT5 python library](https://www.mql5.com/en/docs/python_metatrader5) is [developed specifically for Windows](https://stackoverflow.com/a/59511601/12120015).
