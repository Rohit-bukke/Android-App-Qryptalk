from fastapi import WebSocket
from starlette.websockets import WebSocketState

class ConnectionManager:
    def __init__(self):
        self.active = {}

    async def connect(self, ws: WebSocket, client_id: str):
        await ws.accept()
        self.active[client_id] = ws

    def disconnect(self, client_id):
        self.active.pop(client_id, None)

    async def send(self, data, client_id):
        ws = self.active.get(client_id)
        if ws and ws.client_state == WebSocketState.CONNECTED:
            await ws.send_json(data)

    async def broadcast(self, data):
        for cid in list(self.active.keys()):
            await self.send(data, cid)
