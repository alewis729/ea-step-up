# Expert Advisor (EA)

This is a python script that connects to a websocket server and expects messages that would originally come from TradingView alerts. Those messages are processed to some extent on the server and when this script receives them they are further processed in python and used to open and manage trades on MetaTrader5 (MT5).

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
- Create a `.env` file and add the necessary info (based on `.env.example`)
- You need the webhook/websocket server to be running, either locally or to be publicly accessible.
- The `WS_URL` needs to point to the websocket server.
- Run the script with `python3 src/main.py`
- Simulate sending an alert to the webhook server (via curl for example, with: `curl -X POST http://localhost:3000/webhook -H 'Content-Type: application/json; charset=utf-8' -d '{"text": "BTCUSD Greater Than 9000"}'`; this example won't result in any MT5 operation as it lacks necessary data but you'll see the response in the console)
- The webhook server should receive the alert, and should communicate the necessary information to python. You should be able to see the information on the console that runs python.

### Run operations

- The steps to install and run the script are the same
- For the operations to be handled by this EA you need the alerts received to have all the necessary info:
    - `licenseId`: needs to be the same as the `LICENSE_ID` specified in your `.env`
    - `command`: must be a valid command (see valid commands section)
    - `symbol`: must be a valid symbol that MT5 broker allows for trading
- There is other data that can be sent depending on the commands that you want to execute.
- If you send the alert with the expected data then you should see in the python console the response and in MT5 the operations.

### Valid commands

Valid commands are the commands that come from the `Command` enum from the Node server.

- `BUY`
- `BUYLIMIT`
- `SELL`
- `SELLLIMIT`
- `NEWSLTPLONG`
- `NEWSLTPSHORT`
- `CANCELLONG`
- `CANCELSHORT`
- `CANCELALL`
- `CLOSELONG`
- `CLOSESHORT`
- `CLOSEALL `

#### Alert composition

Alerts can be sent to the webhook in the form of JSON or in the form of plain text. If JSON it's straight forward, the alert expects the info as key-value pairs. If the alert is of plain text form then the data is separated via commas, and the first 3 commands are always `licenseId,command,symbol`. Then, depending on the command the rest of the data should come in this format: `key=value`. Examples:

- plan text: `123456,BUYLIMIT,BTCUSD,risk=0.15,price=60000.05,sl=55123.45,tp=70000,comment="p2.3-BTC-A"`
- plan text: `123321,SELL,BTCUSD,risk=0.1,sl=70000.1,tp=54500,comment="p1.1-BTC-B"`
- json: `{"licenseId":"123123", "command": "CANCELALL", "symbol": "EURUSD.i"}`

### Important note

This project is meant to be ran on Windows OS. It might be possible to run this on macOS or linux but MT5 is meant for Windows and crashes frequently on macOS. Additionally, it seems like the [MT5 python library](https://www.mql5.com/en/docs/python_metatrader5) is [developed specifically for Windows](https://stackoverflow.com/a/59511601/12120015).

### Suggested method of running this EA

There are quite a few parts to this EA and there are a few different ways to run it. It also depends on the actual trading strategy. This is my suggested way to at least begin testing it:

1. Deploy the webhook/websocket server to AWS Lightsail ($5/mo). There are alternatives but what is needed is to make the server URL publicly accessible so that TradingView can send requests to it, and the Python EA can connect to the WebSocket server to receive the messages.
2. Setup MT5 and this Python EA into an other AWS Lightsail VPS (~$10/mo). It needs to be a Windows OS instance so that MT5 and the Python script run reliably and as expected.
3. Let the Python script running on a console, and let MT5 running.
4. Apply your strategy on TradingView (on your local device) and setup/send the alerts based on your strategy. The webhook needs to point to the server URL.

