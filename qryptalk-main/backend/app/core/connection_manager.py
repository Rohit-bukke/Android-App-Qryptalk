"""
WebSocket Connection Manager for QrypTalk.
Handles multi-client asynchronous WebSocket connections, messaging relays, and broadcasts.
"""

from typing import Dict, List, Optional, Any
from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:
    """Manages active WebSocket connections for peer-to-peer secure chat."""

    def __init__(self):
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket, client_id: str):
        """Accepts and stores an incoming WebSocket connection."""
        await ws.accept()
        self.active[client_id] = ws

    def disconnect(self, client_id: str):
        """Removes a client from active connections."""
        self.active.pop(client_id, None)

    async def send(self, data: Dict[str, Any], client_id: str):
        """Sends JSON payload to a specific client if connected."""
        ws = self.active.get(client_id)
        if ws and ws.client_state == WebSocketState.CONNECTED:
            try:
                await ws.send_json(data)
            except Exception as e:
                print(f"[Error] Failed sending to {client_id}: {e}")

    async def broadcast(self, data: Dict[str, Any]):
        """Broadcasts JSON payload to all connected clients."""
        for cid in list(self.active.keys()):
            await self.send(data, cid)

    def get_other_client(self, client_id: str) -> Optional[str]:
        """Returns the ID of the counterpart client in a 2-party chat."""
        for cid in self.active.keys():
            if cid != client_id:
                return cid
        return None


# Global singleton connection manager
manager = ConnectionManager()
