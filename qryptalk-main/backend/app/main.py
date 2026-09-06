"""
QrypTalk Backend Server - Main Application Entrypoint.
FastAPI server orchestrating Quantum Random Number Generation (QRNG),
Variational Quantum Machine Learning (QML) threat intelligence, BB84 key distribution,
and encrypted WebSocket communication.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.quantum.routers.websocket import router as websocket_router
from app.core.quantum.routers.quantum_api import router as quantum_api_router

app = FastAPI(
    title="QrypTalk Quantum & QML Backend",
    description="High-fidelity BB84 Quantum Key Distribution server powered by Quantum Superposition QRNG and Variational Quantum Machine Learning (QML) threat intelligence.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local cross-origin connections and Android emulators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket and REST endpoints
app.include_router(websocket_router)
app.include_router(quantum_api_router)


@app.get("/")
def root():
    return {
        "project": "QrypTalk",
        "system": "Quantum Key Distribution & QML Threat Intelligence Server",
        "version": "2.0.0",
        "documentation": "/docs",
        "subsystems": {
            "qrng": "/api/quantum/qrng/bits",
            "qml_prediction": "/api/quantum/qml/predict",
            "bb84_simulation": "/api/quantum/bb84/simulate",
            "session_status": "/api/quantum/session",
            "websocket": "/ws/{client_id}",
        },
    }   
