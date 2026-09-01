"""
QrypTalk Server Runner.
Launches the FastAPI backend with Uvicorn.
Can be run directly with: `python bb84_server.py` or `uvicorn bb84_server:app --reload --host 0.0.0.0`
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("=" * 65)
    print("  QRYPTALK: Quantum Key Distribution (BB84) + QML Server")
    print("  - QRNG Statevector Superposition Engine: ACTIVE")
    print("  - Variational Quantum Machine Learning (VQC): ACTIVE")
    print("  - Real-Time Channel Threat Classification: ACTIVE")
    print("=" * 65)
    uvicorn.run("bb84_server:app", host="0.0.0.0", port=8000, reload=True)
