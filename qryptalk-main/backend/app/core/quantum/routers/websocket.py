from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from app.core.connection_manager import ConnectionManager
from app.quantum.bb84 import generate_bb84_key
from app.core.session_manager import session_manager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def ws_endpoint(ws: WebSocket, client_id: str):

    await manager.connect(ws, client_id)

    if len(manager.active) == 2:
        key, qber, status = await asyncio.to_thread(generate_bb84_key)

        session_manager.key = key
        session_manager.qber = qber

        await manager.broadcast({
            "type": "key_exchange",
            "qber": round(qber, 4),
            "status": status
        })

    try:
        while True:
            data = await ws.receive_json()

            other = next((c for c in manager.active if c != client_id), None)

            if other:
                await manager.send({
                    "type": "encrypted_message",
                    "ciphertext": data["ciphertext"]
                }, other)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
