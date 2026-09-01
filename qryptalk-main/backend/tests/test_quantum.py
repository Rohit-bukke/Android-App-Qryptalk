"""
Comprehensive Unit & Integration Test Suite for QrypTalk Quantum & QML Subsystems.
"""

import unittest
import numpy as np

from app.core.quantum.circuit import QuantumCircuit
from app.core.quantum.qrng import QuantumRandomNumberGenerator, qrng
from app.core.quantum.qml_model import VariationalQuantumClassifier, qml_classifier
from app.core.quantum.bb84 import generate_bb84_key
from app.main import app
from fastapi.testclient import TestClient


class TestQuantumCircuit(unittest.TestCase):
    """Tests the statevector quantum circuit simulator."""

    def test_hadamard_superposition(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        probs = qc.get_probabilities()
        self.assertEqual(len(probs), 2)
        self.assertAlmostEqual(probs[0], 0.5, places=5)
        self.assertAlmostEqual(probs[1], 0.5, places=5)
        self.assertAlmostEqual(qc.expectation_z(0), 0.0, places=5)

    def test_pauli_x_flip(self):
        qc = QuantumCircuit(1)
        qc.x(0)
        probs = qc.get_probabilities()
        self.assertAlmostEqual(probs[0], 0.0, places=5)
        self.assertAlmostEqual(probs[1], 1.0, places=5)
        self.assertAlmostEqual(qc.expectation_z(0), -1.0, places=5)

    def test_bell_state_entanglement(self):
        # Create Bell state (|00> + |11>) / sqrt(2)
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        probs = qc.get_probabilities()
        self.assertAlmostEqual(probs[0], 0.5, places=5)  # |00>
        self.assertAlmostEqual(probs[1], 0.0, places=5)  # |01>
        self.assertAlmostEqual(probs[2], 0.0, places=5)  # |10>
        self.assertAlmostEqual(probs[3], 0.5, places=5)  # |11>

    def test_rotations(self):
        qc = QuantumCircuit(1)
        qc.ry(np.pi / 2, 0)
        probs = qc.get_probabilities()
        self.assertAlmostEqual(probs[0], 0.5, places=4)
        self.assertAlmostEqual(probs[1], 0.5, places=4)


class TestQRNG(unittest.TestCase):
    """Tests the Quantum Random Number Generator."""

    def test_generate_bits_shape_and_values(self):
        generator = QuantumRandomNumberGenerator(register_size=8)
        bits = generator.generate_bits(512)
        self.assertEqual(len(bits), 512)
        self.assertTrue(set(bits).issubset({0, 1}))

    def test_entropy_evaluation(self):
        generator = QuantumRandomNumberGenerator(register_size=8)
        bits = generator.generate_bits(2048)
        entropy_data = generator.evaluate_entropy(bits)

        self.assertIn("shannon_entropy", entropy_data)
        self.assertGreaterEqual(entropy_data["shannon_entropy"], 0.95)
        self.assertGreaterEqual(entropy_data["min_entropy"], 0.80)
        self.assertTrue(0.40 <= entropy_data["ones_ratio"] <= 0.60)

    def test_generate_hex_key(self):
        generator = QuantumRandomNumberGenerator(register_size=8)
        key_hex = generator.generate_hex_key(32)  # 256 bits = 64 hex chars
        self.assertEqual(len(key_hex), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in key_hex))


class TestVariationalQMLModel(unittest.TestCase):
    """Tests the Variational Quantum Classifier (QML) Model."""

    def test_qml_forward_pass_probabilities(self):
        vqc = VariationalQuantumClassifier(num_qubits=4, num_layers=2)
        features = np.array([0.02, 0.50, 0.99, 0.01])  # Pristine channel
        probs = vqc.predict_proba(features)

        self.assertEqual(len(probs), 4)
        self.assertAlmostEqual(float(np.sum(probs)), 1.0, places=5)
        self.assertTrue(all(p >= 0 for p in probs))

    def test_pristine_channel_classification(self):
        # QBER = 0.01 (Pristine channel) -> Should classify as SECURE_OPTIMAL
        result = qml_classifier.classify_channel(qber=0.01, sift_ratio=0.5)
        self.assertEqual(result["predicted_class"], "SECURE_OPTIMAL")
        self.assertTrue(result["is_secure"])
        self.assertGreaterEqual(result["confidence"], 0.5)

    def test_eavesdropper_detection_classification(self):
        # QBER = 0.25 (Classic BB84 intercept-resend attack) -> Should detect eavesdropper
        result = qml_classifier.classify_channel(qber=0.25, sift_ratio=0.48)
        self.assertIn(result["predicted_class"], ["ACTIVE_EAVESDROPPER", "CRITICAL_ATTACK"])
        self.assertFalse(result["is_secure"])


class TestBB84Protocol(unittest.TestCase):
    """Tests the enhanced BB84 protocol powered by QRNG and QML."""

    def test_bb84_secure_scenario(self):
        key, qber, status, telemetry = generate_bb84_key(n_bits=512, eve_enabled=False)
        self.assertIsNotNone(key)
        self.assertEqual(len(key), 64)  # 256-bit SHA-256 hex digest
        self.assertLess(qber, 0.15)
        self.assertTrue(telemetry["is_secure"])
        self.assertEqual(telemetry["predicted_class"], "SECURE_OPTIMAL")

    def test_bb84_eavesdropping_scenario(self):
        key, qber, status, telemetry = generate_bb84_key(n_bits=512, eve_enabled=True)
        self.assertIsNone(key)
        self.assertGreater(qber, 0.15)
        self.assertFalse(telemetry["is_secure"])
        self.assertIn("Security Alert", status)


class TestFastAPIEndpoints(unittest.TestCase):
    """Tests the FastAPI REST endpoints."""

    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("QrypTalk", response.json()["project"])

    def test_qrng_bits_api(self):
        response = self.client.post("/api/quantum/qrng/bits", json={"count": 128})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["length"], 128)
        self.assertIn("shannon_entropy", data["entropy_analysis"])

    def test_qml_predict_api(self):
        payload = {
            "qber": 0.24,
            "sift_ratio": 0.5,
            "basis_entropy": 0.99,
            "error_asymmetry": 0.02,
        }
        response = self.client.post("/api/quantum/qml/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_secure"])
        self.assertIn(data["predicted_class"], ["ACTIVE_EAVESDROPPER", "CRITICAL_ATTACK"])

    def test_bb84_simulate_api(self):
        payload = {"n_bits": 256, "eve_enabled": False, "qber_sample_size": 0.5}
        response = self.client.post("/api/quantum/bb84/simulate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["derived_aes_key"])


if __name__ == "__main__":
    unittest.main()
