# import asyncio
# import json
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import numpy as np
# from starlette.websockets import WebSocketState

# app = FastAPI(title="QKD Chat Server")

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: dict[str, WebSocket] = {}

#     async def connect(self, websocket: WebSocket, client_id: str):
#         await websocket.accept()
#         self.active_connections[client_id] = websocket

#     def disconnect(self, client_id: str):
#         if client_id in self.active_connections:
#             del self.active_connections[client_id]

#     async def send_json(self, data: dict, client_id: str):
#         websocket = self.active_connections.get(client_id)
#         if websocket and websocket.client_state == WebSocketState.CONNECTED:
#             try:
#                 await websocket.send_json(data)
#             except Exception as e:
#                 print(f"Could not send to {client_id}. Error: {e}")

#     async def broadcast_json(self, data: dict):
#         for client_id in list(self.active_connections.keys()):
#             await self.send_json(data, client_id)

# manager = ConnectionManager()

# def generate_bb84_key(n_bits=256, eavesdropper_present=True, qber_sample_size=0.5):
#     """
#     Simulates BB84 using a direct mathematical/probabilistic model.
#     This version is faster and avoids the Qiskit simulator bug.
#     """
#     print("\n" + "="*50)
#     print(" STEP 1: INITIAL KEY & BASIS GENERATION")
#     print("="*50)
#     print(f"Simulating with eavesdropper_present = {eavesdropper_present}")
    
#     # 1. Alice generates her random bits and bases
#     alice_bits = np.random.randint(2, size=n_bits)
#     alice_bases = np.random.randint(2, size=n_bits) # 0 for Z-basis (+), 1 for X-basis (x)
#     print(f"Alice generated {n_bits} random bits and bases.")
#     print(f"  - Alice's bits (sample): {alice_bits[:10]}...")
#     print(f"  - Alice's bases (sample): {alice_bases[:10]}...")
    
#     # 2. Bob chooses his random bases
#     bob_bases = np.random.randint(2, size=n_bits)
#     print(f"Bob generated {n_bits} random measurement bases.")
#     print(f"  - Bob's bases (sample):   {bob_bases[:10]}...")
    
#     bob_results = np.zeros(n_bits, dtype=int)

#     # 3. Simulate the transmission and measurement
#     print("\n" + "="*50)
#     print(" STEP 2: SIMULATING THE QUANTUM CHANNEL")
#     print("="*50)
#     if eavesdropper_present:
#         print("An eavesdropper (Eve) is present and will intercept each qubit.")
#     else:
#         print("The channel is secure. No eavesdropper is present.")

#     for i in range(n_bits):
#         qubit_from_alice = alice_bits[i]
        
#         # --- EVE'S INTERCEPTION ---
#         if eavesdropper_present:
#             eve_bases = np.random.randint(2, size=n_bits)
#             if alice_bases[i] != eve_bases[i]:
#                 if np.random.random() < 0.5:
#                     qubit_from_alice = 1 - qubit_from_alice
        
#         if alice_bases[i] != bob_bases[i]:
#              bob_results[i] = np.random.randint(2)
#         else:
#              bob_results[i] = qubit_from_alice

#     # 4. Sifting and QBER Calculation
#     print("\n" + "="*50)
#     print(" STEP 3: SIFTING AND QBER CHECK")
#     print("="*50)
#     sifted_indices = np.where(alice_bases == bob_bases)[0]
#     print(f"Alice and Bob compared bases. They matched on {len(sifted_indices)} bits.")
    
#     if len(sifted_indices) < 20:
#         return None, 1.0, "Key generation failed: not enough matching bases."

#     num_sample_bits = max(1, int(len(sifted_indices) * qber_sample_size))
#     if num_sample_bits >= len(sifted_indices):
#         num_sample_bits = len(sifted_indices) // 2

#     sample_indices = np.random.choice(sifted_indices, size=num_sample_bits, replace=False)
#     print(f"They will now publicly compare {num_sample_bits} of these bits to check for errors.")
    
#     mismatches = sum(1 for i in sample_indices if alice_bits[i] != bob_results[i])
#     qber = mismatches / num_sample_bits if num_sample_bits > 0 else 0
#     print(f"Comparison complete. Found {mismatches} mismatches.")
#     print(f"Calculated QBER = {qber:.2%}")
    
#     # 5. Security Check
#     print("\n" + "="*50)
#     print(" STEP 4: SECURITY VALIDATION & FINAL KEY")
#     print("="*50)
#     security_threshold = 0.15
#     if qber > security_threshold:
#         print(f"RESULT: QBER is above the {security_threshold:.0%} threshold. Eavesdropper detected!")
#         return None, qber, f"Eavesdropper Detected! QBER ({qber:.2%}) is above threshold. Key discarded."
#     else:
#         print(f"RESULT: QBER is within the secure threshold. Key is considered secure.")
#         final_key_indices = np.setdiff1d(sifted_indices, sample_indices)
#         final_key = "".join(str(alice_bits[i]) for i in final_key_indices)
#         print(f"Generated Final Secure Key of length {len(final_key)}.")
#         return final_key, qber, f"Key Secure. QBER ({qber:.2%}) is below threshold."


# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     await manager.connect(websocket, client_id)
#     print(f"\n[+] Client connected: {client_id}. Total clients: {len(manager.active_connections)}")

#     if len(manager.active_connections) == 2:
#         print("\n[*] Two clients detected. Starting BB84 key exchange simulation...")
        
#         # Change this flag to True to demonstrate eavesdropper detection
#         final_key, qber, status_message = await asyncio.to_thread(
#             generate_bb84_key, eavesdropper_present=False
#         )
        
#         print(f"\n[*] Key generation process finished. Result: {status_message}")
#         print("[*] Broadcasting results to both clients...")
        
#         key_distribution_payload = {
#             "type": "key_exchange",
#             "key": final_key,
#             "qber": round(qber, 4),
#             "status": status_message
#         }
#         await manager.broadcast_json(key_distribution_payload)

#     try:
#         while True:
#             encrypted_data = await websocket.receive_json()
#             print(f"\n[+] Received encrypted JSON from '{client_id}':")
#             print(f"    Ciphertext: {encrypted_data.get('ciphertext')[:30]}...")

#             recipient_id = next((c_id for c_id in manager.active_connections if c_id != client_id), None)
            
#             if recipient_id:
#                 print(f"[*] Relaying message from '{client_id}' to '{recipient_id}'...")
#                 message_payload = {
#                     "type": "encrypted_message",
#                     "sender": client_id,
#                     "ciphertext": encrypted_data.get('ciphertext')
#                 }
#                 await manager.send_json(message_payload, recipient_id)

#     except (WebSocketDisconnect, RuntimeError):
#         manager.disconnect(client_id)
#         print(f"\n[-] Client {client_id} disconnected. Total clients: {len(manager.active_connections)}")
#         await manager.broadcast_json({
#             "type": "user_status",
#             "message": f"{client_id} has left the chat."
#         })


