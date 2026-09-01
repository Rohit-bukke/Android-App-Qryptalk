"""
REST API Endpoints for Quantum Operations, QRNG, and QML Threat Intelligence in QrypTalk.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import numpy as np

from app.core.quantum.qrng import qrng
from app.core.quantum.qml_model import qml_classifier
from app.core.quantum.bb84 import generate_bb84_key
from app.core.session_manager import session_manager

router = APIRouter(prefix="/api/quantum", tags=["Quantum & QML Operations"])


# ------------------- Request/Response Schemas ------------------- #

class QRNGRequest(BaseModel):
    count: int = Field(256, ge=1, le=16384, description="Number of quantum random bits to generate")


class QRNGResponse(BaseModel):
    bits: str
    length: int
    entropy_analysis: Dict[str, Any]


class QRNGBytesRequest(BaseModel):
    num_bytes: int = Field(32, ge=1, le=2048, description="Number of quantum random bytes to generate")


class QRNGBytesResponse(BaseModel):
    hex_string: str
    num_bytes: int
    bit_length: int
    entropy_analysis: Dict[str, Any]


class QMLPredictRequest(BaseModel):
    qber: float = Field(..., ge=0.0, le=1.0, description="Quantum Bit Error Rate (0.0 to 1.0)")
    sift_ratio: float = Field(0.5, ge=0.0, le=1.0, description="Ratio of sifted bits to transmitted bits")
    basis_entropy: float = Field(1.0, ge=0.0, le=1.0, description="Shannon entropy of basis selection")
    error_asymmetry: float = Field(0.0, ge=-1.0, le=1.0, description="Error asymmetry between X and Z bases")


class BB84SimulateRequest(BaseModel):
    n_bits: int = Field(256, ge=32, le=4096, description="Total quantum bits exchanged")
    eve_enabled: bool = Field(False, description="Simulate an active eavesdropper (Eve)")
    qber_sample_size: float = Field(0.5, ge=0.1, le=0.9, description="Fraction of sifted bits for QBER check")


# ------------------- Endpoints ------------------- #

@router.get("/health")
def quantum_health():
    """Returns the operational status of the QRNG and QML subsystems."""
    return {
        "status": "online",
        "qrng_engine": "QuantumCircuit Statevector Superposition",
        "qml_classifier": "Variational Quantum Circuit (4-Qubit PQC)",
        "ansatz_layers": qml_classifier.num_layers,
        "security_classes": qml_classifier.CLASS_NAMES,
    }


@router.post("/qrng/bits", response_model=QRNGResponse)
def generate_quantum_bits(request: QRNGRequest):
    """
    Generates non-deterministic bits using quantum superposition (Hadamard gate) and measurement collapse.
    Includes full NIST-inspired entropy analysis.
    """
    raw_bits = qrng.generate_bits(request.count)
    entropy_info = qrng.evaluate_entropy(raw_bits)
    bit_str = "".join(str(b) for b in raw_bits)

    return QRNGResponse(
        bits=bit_str,
        length=len(bit_str),
        entropy_analysis=entropy_info,
    )


@router.post("/qrng/bytes", response_model=QRNGBytesResponse)
def generate_quantum_bytes(request: QRNGBytesRequest):
    """Generates cryptographic-grade random hex keys derived from quantum entropy."""
    raw_bytes = qrng.generate_bytes(request.num_bytes)
    raw_bits = np.unpackbits(np.frombuffer(raw_bytes, dtype=np.uint8))
    entropy_info = qrng.evaluate_entropy(raw_bits)

    return QRNGBytesResponse(
        hex_string=raw_bytes.hex(),
        num_bytes=request.num_bytes,
        bit_length=request.num_bytes * 8,
        entropy_analysis=entropy_info,
    )


@router.post("/qml/predict")
def predict_channel_threat(request: QMLPredictRequest):
    """
    Executes the Variational Quantum Machine Learning (QML) classifier
    on supplied quantum channel parameters to detect eavesdropping and anomalies.
    """
    prediction = qml_classifier.classify_channel(
        qber=request.qber,
        sift_ratio=request.sift_ratio,
        basis_entropy=request.basis_entropy,
        error_asymmetry=request.error_asymmetry,
    )
    return prediction


@router.get("/qml/metadata")
def get_qml_metadata():
    """Returns the architectural design and parameter specifications of the QML model."""
    return {
        "model_type": "Variational Quantum Classifier (VQC)",
        "num_qubits": qml_classifier.num_qubits,
        "num_layers": qml_classifier.num_layers,
        "total_trainable_parameters": qml_classifier.num_params,
        "embedding_method": "Angle Embedding (Ry, Rz rotations)",
        "entanglement_gates": "Circular CNOT Ring Ladder",
        "observable": "Pauli-Z Expectation Values <Z_i>",
        "classes": qml_classifier.CLASS_NAMES,
    }


@router.post("/bb84/simulate")
def simulate_bb84(request: BB84SimulateRequest):
    """
    Runs a full BB84 Quantum Key Distribution protocol simulation
    integrated with QRNG and real-time QML threat classification.
    """
    key, qber, status, qml_telemetry = generate_bb84_key(
        n_bits=request.n_bits,
        eve_enabled=request.eve_enabled,
        qber_sample_size=request.qber_sample_size,
    )

    return {
        "success": bool(key is not None),
        "derived_aes_key": key,
        "qber": round(qber, 4),
        "status_message": status,
        "eve_enabled": request.eve_enabled,
        "qml_telemetry": qml_telemetry,
    }


@router.get("/session")
def get_current_session():
    """Returns the current active shared key and telemetry history."""
    return {
        "has_active_key": bool(session_manager.key is not None),
        "active_key": session_manager.key,
        "last_qber": session_manager.qber,
        "last_status": session_manager.status,
        "last_qml_telemetry": session_manager.qml_telemetry,
        "history": session_manager.session_history,
    }
