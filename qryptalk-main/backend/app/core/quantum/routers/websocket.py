"""
WebSocket Router for Real-Time QKD Chat and Quantum Telemetry Streaming.
Relays end-to-end encrypted messages and streams live QML threat assessments.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from app.core.connection_manager import manager
from app.core.quantum.bb84 import generate_bb84_key
from app.core.session_manager import session_manager

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for mobile clients:
    1. Connects clients and maintains active connection map.
    2. When two clients connect, automatically orchestrates QRNG-based BB84 key exchange
       and evaluates channel security using the Variational Quantum Machine Learning (QML) model.
    3. Relays AES-GCM encrypted message payloads between parties.
    """
    await manager.connect(websocket, client_id)
    print(f"[+] Client connected: {client_id} (Total: {len(manager.active)})")

    # Notify connected client of their status
    await manager.send({
        "type": "connection_ack",
        "client_id": client_id,
        "active_clients": list(manager.active.keys()),
        "message": f"Connected to QrypTalk Quantum Server as '{client_id}'."
    }, client_id)

    # When 2 clients are present, trigger BB84 key exchange simulation
    if len(manager.active) == 2:
        print("[*] Two clients connected. Initiating QRNG-powered BB84 Key Exchange with QML Intelligence...")

        # Run non-blocking key generation in worker thread
        key, qber, status_message, qml_telemetry = await asyncio.to_thread(
            generate_bb84_key, n_bits=256, eve_enabled=False
        )

        session_manager.update_session(
            key=key,
            qber=qber,
            status=status_message,
            qml_telemetry=qml_telemetry,
        )

        payload = {
            "type": "key_exchange",
            "key": key,
            "qber": round(qber, 4),
            "status": status_message,
            "is_secure": qml_telemetry.get("is_secure", qber < 0.15),
            "qml_state": qml_telemetry.get("predicted_class"),
            "qml_confidence": qml_telemetry.get("confidence"),
            "qml_telemetry": qml_telemetry,
        }

        print(f"[*] Broadcasting Key Exchange Result: {status_message}")
        await manager.broadcast(payload)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "encrypted_message")

            if msg_type == "renegotiate_key":
                # Client requested key re-exchange (e.g. toggle Eve or refresh session)
                eve_flag = bool(data.get("eve_enabled", False))
                key, qber, status_message, qml_telemetry = await asyncio.to_thread(
                    generate_bb84_key, n_bits=256, eve_enabled=eve_flag
                )
                session_manager.update_session(key, qber, status_message, qml_telemetry)
                await manager.broadcast({
                    "type": "key_exchange",
                    "key": key,
                    "qber": round(qber, 4),
                    "status": status_message,
                    "is_secure": qml_telemetry.get("is_secure", qber < 0.15),
                    "qml_state": qml_telemetry.get("predicted_class"),
                    "qml_confidence": qml_telemetry.get("confidence"),
                    "qml_telemetry": qml_telemetry,
                })

            elif msg_type == "encrypted_message":
                # Relay ciphertext to the peer
                other_client = manager.get_other_client(client_id)
                if other_client:
                    await manager.send({
                        "type": "encrypted_message",
                        "sender": client_id,
                        "ciphertext": data.get("ciphertext"),
                        "iv": data.get("iv", ""),
                        "tag": data.get("tag", ""),
                    }, other_client)

    except (WebSocketDisconnect, RuntimeError):
        manager.disconnect(client_id)
        session_manager.reset()
        print(f"[-] Client disconnected: {client_id}")
        await manager.broadcast({
            "type": "user_status",
            "message": f"Client '{client_id}' disconnected.",
            "active_clients": list(manager.active.keys()),
        })
