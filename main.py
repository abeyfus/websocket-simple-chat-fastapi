import json
import logging
from contextlib import suppress

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)

USERS = {}
HISTORY = {}

app = FastAPI()

templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chatname: str):
        await websocket.accept()
        if chatname not in self.active_connections:
            self.active_connections[chatname] = []
        self.active_connections[chatname].append(websocket)

        if chatname in HISTORY:
            for message in HISTORY[chatname]:
                await websocket.send_text(json.dumps(message))

    def disconnect(self, websocket: WebSocket, chatname: str):
        self.active_connections[chatname].remove(websocket)
        with suppress(KeyError):
            del USERS[websocket]

    async def send_message(self, chatname: str, message: str):
        for connection in self.active_connections[chatname]:
            await connection.send_text(message)

    async def send_file(self, chatname: str, data: bytes):
        for connection in self.active_connections[chatname]:
            await connection.send_bytes(data)


manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat/{chatname}/")
async def get(request: Request, chatname: str):
    return templates.TemplateResponse("room.html", {"request": request, "chatname": chatname})


@app.websocket("/ws/chat/{chatname}/")
async def websocket_endpoint(websocket: WebSocket, chatname: str):
    await manager.connect(websocket, chatname)
    try:
        while True:
            message = await websocket.receive()
            websocket._raise_on_disconnect(message)
            if 'text' in message:
                text_data = message['text']

                with suppress(json.decoder.JSONDecodeError, KeyError):
                    text_data_json = json.loads(text_data)

                    logger.info(text_data_json)

                    if command := text_data_json.get('command'):
                        if command == 'auth':
                            user = text_data_json['username']
                            if user not in USERS.values():
                                USERS[websocket] = user
                            else:
                                await websocket.send_text(
                                    json.dumps({'type': 'error_message', 'error': f'User `{user}` already exists'})
                                )
                        elif command == 'sendmessage':
                            user = USERS.get(websocket)
                            if user:
                                message = text_data_json['message']

                                # Send message to room group
                                await manager.send_message(
                                    chatname, json.dumps({'username': user, 'message': message})
                                )
                                if chatname not in HISTORY:
                                    HISTORY[chatname] = []
                                HISTORY[chatname].append({'username': user, 'message': message})
            elif 'bytes' in message:
                await manager.send_message(
                    chatname, json.dumps({'username': user, 'message': 'user sent file:'})
                )
                bytes_data = message['bytes']
                await manager.send_file(chatname, bytes_data)

    except WebSocketDisconnect:
        manager.disconnect(websocket, chatname)