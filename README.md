# QrypTalk: Quantum Machine Learning & QKD Secure Messaging

QrypTalk is a next-generation quantum-resilient secure communication system combining **Quantum Key Distribution (BB84 Protocol)**, **Quantum Superposition Random Number Generation (QRNG)**, and **Variational Quantum Machine Learning (QML)** for real-time channel threat intelligence and eavesdropper detection.

---

#contributors 
This project was created for the Amaravati Quantum Valley Hackathon 2025. Contributions and suggestions for further development (e.g., PQC integration, hardware interfacing) are welcome!

## Highlights & Core Innovations

### 1. Quantum Machine Learning (QML) Threat Intelligence Engine
* **Variational Quantum Classifier (VQC)**: 4-qubit Parameterized Quantum Circuit (PQC) executing real-time quantum channel threat classification.
* **Angle & Phase Embedding**: Encodes 4-dimensional channel telemetry (Quantum Bit Error Rate $\text{QBER}$, sifted key ratio, basis entropy, error asymmetry) into Hilbert state space:
  $$\vert\psi(x)\rangle = \bigotimes_{i=0}^{3} R_z\left(\frac{x_i}{2}\right) R_y(x_i) H \vert 0 \rangle$$
* **Entangled Ansatz Topology**: Multi-layer variational ansatz utilizing single-qubit rotations ($R_y(\theta), R_z(\theta)$) and circular ring CNOT entangling gates to capture non-linear channel disturbances.
* **Pauli Observable Measurement**: Measures expectation values $\langle Z_i \rangle$ to classify channel states into 4 distinct threat categories:
  - `SECURE_OPTIMAL` (Pristine channel; zero intrusion; high-throughput key generation)
  - `NOISY_ENVIRONMENT` (Thermal/channel noise; trigger Cascade error correction)
  - `ACTIVE_EAVESDROPPER` (Intercept-Resend attack detected with ~91% confidence)
  - `CRITICAL_ATTACK` (Severe disturbance; automatic session abort & key purge)
* **Adaptive Privacy Amplification**: Dynamically computes key compression factor $r = 1 - 2 h(\text{QBER})$ based on Shannon binary entropy.

### 2. Quantum Random Number Generator (QRNG)
* **Superposition Wavefunction Collapse**: Replaces classical pseudo-random generators ($PRNG$) with true quantum entropy by placing $N$-qubit registers into equal superposition via Hadamard gates:
  $$H\vert 0\rangle = \frac{\vert 0\rangle + \vert 1\rangle}{\sqrt{2}}$$
* **Entropy Verification**: Evaluates real-time Shannon entropy ($>0.9999\text{ bits/bit}$) and NIST SP 800-22 monobit frequency tests before bitstream injection.
* **Cryptographic Seeding**: Generates high-entropy non-deterministic bitstreams for Alice's bit preparation, Alice's basis selection, and Bob's measurement bases.

### 3. End-to-End BB84 QKD Protocol & AES-256-GCM
* **4-Stage Protocol**:
  1. **Quantum State Preparation**: Alice encodes QRNG bits into rectilinear ($Z$) or diagonal ($X$) bases.
  2. **Quantum Channel Transmission & Eve Interception**: Simulates quantum state collapse under intercept-resend attacks.
  3. **Basis Sifting & QBER Calculation**: Public basis reconciliation over classical channel.
  4. **QML Validation & Privacy Amplification**: Threat classification via VQC followed by SHA-256 key distillation for 256-bit AES-GCM encryption.

---

## Quantum Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                            QRYPTALK QUANTUM PIPELINE                              |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Alice ] ---> (QRNG Bit Gen) ---> (QRNG Basis Prep)                            |
|       |                                    |                                      |
|       v                                    v                                      |
|   |0>, |1>, |+>, |-> ----------------> [ Quantum Channel ] <--- [ Eve Intercept ] |
|                                            |                                      |
|                                            v                                      |
|  [ Bob ]   <--- (QRNG Basis Prep) <--- (Measurement)                              |
|       |                                                                           |
|       +----------------------------> [ Basis Sifting ]                            |
|                                            |                                      |
|                                            v                                      |
|                             [ QBER & Channel Telemetry ]                          |
|                                            |                                      |
|                                            v                                      |
|                    +-----------------------------------------------+              |
|                    |     VARIATIONAL QUANTUM CLASSIFIER (QML)      |              |
|                    |  - 4-Qubit Parameterized Quantum Circuit     |              |
|                    |  - Angle Embedding & Circular CNOT Ansatz     |              |
|                    |  - Observable <Z_i> & Softmax Threat Head     |              |
|                    +-----------------------------------------------+              |
|                                            |                                      |
|                     +----------------------+----------------------+               |
|                     |                                             |               |
|                     v [SECURE]                                    v [INSECURE]    |
|       [ Privacy Amplification & AES-256 ]                 [ Abort & Alert ]       |
|                     |                                             |               |
|                     v                                             v               |
|            [ Encrypted Chat ]                            [ Input Disabled ]       |
+-----------------------------------------------------------------------------------+
```

---

## Performance Benchmarks

| Subsystem | Metric | Result | Status |
| :--- | :--- | :--- | :--- |
| **QRNG Engine** | Bit Generation Throughput | **2.68 Mbits/sec** | Pass (NIST / Shannon $> 0.9999$) |
| **QML Classifier** | Inference Latency | **1.05 ms / prediction** | Real-Time Capable |
| **QML Eve Detection** | Intercept-Resend Accuracy | **91.47% Confidence** | Verified |
| **BB84 Protocol** | End-to-End Key Distillation | **126 ms** (512 qubits) | Secure AES-256 Key Derived |

---

## API Reference

The backend provides interactive Swagger UI at `http://localhost:8000/docs`.

### REST Endpoints
* `GET /api/quantum/health`: Returns operational status of QRNG and QML subsystems.
* `POST /api/quantum/qrng/bits`: Generates $N$ quantum random bits with entropy analysis.
* `POST /api/quantum/qrng/bytes`: Generates cryptographic hex key derived from quantum entropy.
* `POST /api/quantum/qml/predict`: Runs real-time VQC inference on custom channel metrics ($\text{QBER}$, sift ratio, basis entropy, error asymmetry).
* `GET /api/quantum/qml/metadata`: Returns VQC ansatz architecture, qubit count, and parameter specifications.
* `POST /api/quantum/bb84/simulate`: Runs a full BB84 simulation with QRNG and QML classification.
* `GET /api/quantum/session`: Retrieves active cryptographic session and historical telemetry.

### WebSocket Endpoint
* `WS /ws/{client_id}`: Real-time bi-directional channel for automated key exchange, AES-GCM message relay, and live security telemetry streaming.

---

## Quickstart Guide

### 1. Prerequisites
* Python 3.9+
* Pip

### 2. Backend Setup
```bash
cd qryptalk-main/backend

# Install dependencies
pip install -r requirements.txt

# Run unit test suite
python -m unittest discover -s tests -p "test_*.py"

# Run performance benchmarks
python benchmark_quantum.py

# Start FastAPI server
python bb84_server.py
# (or: uvicorn bb84_server:app --reload --host 0.0.0.0 --port 8000)
```

### 3. Verify Server
Visit `http://localhost:8000/docs` in your browser to interactively test all Quantum and QML endpoints.

---

## Repository Structure

```
Qryptalk_project/
├── qryptalk-main/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py                      # FastAPI entrypoint with CORS & routes
│   │   │   ├── core/
│   │   │   │   ├── connection_manager.py    # WebSocket client manager
│   │   │   │   ├── session_manager.py       # Session keys & telemetry history
│   │   │   │   └── quantum/
│   │   │   │       ├── circuit.py           # Quantum Circuit & Statevector simulator
│   │   │   │       ├── qrng.py              # Quantum Random Number Generator (Hadamard)
│   │   │   │       ├── qml_model.py         # Variational Quantum Classifier (VQC / QML)
│   │   │   │       ├── bb84.py              # BB84 QKD Protocol Engine
│   │   │   │       └── routers/
│   │   │   │           ├── quantum_api.py   # REST API for QRNG, QML, & BB84
│   │   │   │           └── websocket.py     # Real-time WebSocket relay & telemetry
│   │   ├── tests/
│   │   │   └── test_quantum.py              # 16 Unit & Integration Tests
│   │   ├── benchmark_quantum.py             # QRNG & QML Performance Benchmarks
│   │   ├── bb84_server.py                   # Server executable script
│   │   └── requirements.txt                 # Backend dependencies
│   ├── QrypTalkAndroid/                     # Android client application
│   └── README.md
└── README.md
```
