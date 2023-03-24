import json
import websocket
from threading import Thread
import sys
import time
from contextlib import suppress


def on_message(ws, message):
    global username
    with suppress(json.decoder.JSONDecodeError, KeyError):
        message_json = json.loads(message)
        if 'username' in message_json:
            print(f"{message_json['username']} > {message_json['message']}")
        elif 'error' in message_json:
            print(message_json['error'])
            username = None


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        global username
        time.sleep(1)
        username = input("Please enter username: ")
        ws.send(json.dumps({'command': 'auth', 'username': username}))
        while(True):
            time.sleep(1)
            if username:
                message = input()
                ws.send(json.dumps({'command': 'sendmessage',  'message': message}))
            else:
                username = input("Please enter username: ")
                ws.send(json.dumps({'command': 'auth', 'username': username}))

    Thread(target=run).start()


if __name__ == "__main__":
    # websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = "ws://51.250.3.81:8000/ws/chat/myroom/"
    else:
        host = sys.argv[1]
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
