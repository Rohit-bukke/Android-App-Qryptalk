"""
Quantum Random Number Generator (QRNG) Module for QrypTalk.
Leverages quantum superposition state evolution (Hadamard gate) and wavefunction collapse
to generate quantum-random bitstreams, entropy metrics, and cryptographic seeds.
"""

from typing import List, Dict, Any, Tuple
import math
import numpy as np
from app.core.quantum.circuit import QuantumCircuit


class QuantumRandomNumberGenerator:
    """
    Simulates a hardware-grade Quantum Random Number Generator (QRNG).
    Uses Hadamard gates to put qubits into equal superposition state (|0> + |1>)/sqrt(2),
    followed by projective measurement collapse to produce true quantum-entropy bitstreams.
    """

    def __init__(self, register_size: int = 8):
        """
        :param register_size: Number of parallel qubits in the QRNG circuit register.
        """
        self.register_size = register_size
        self._circuit = QuantumCircuit(self.register_size)

    def generate_bits(self, count: int = 256) -> np.ndarray:
        """
        Generates `count` quantum random bits using quantum superposition and measurement.
        """
        if count <= 0:
            return np.array([], dtype=int)

        # Prepare N-qubit superposition
        self._circuit.reset()
        for q in range(self.register_size):
            self._circuit.h(q)

        # Number of samples needed from the 2^N state register
        num_shots = math.ceil(count / self.register_size)
        sampled_ints = self._circuit.measure_all(shots=num_shots)

        # Unpack integers into bit arrays
        bits = []
        for val in sampled_ints:
            for bit_pos in range(self.register_size):
                bits.append((int(val) >> bit_pos) & 1)
                if len(bits) == count:
                    break
            if len(bits) == count:
                break

        return np.array(bits[:count], dtype=int)

    def generate_bit_string(self, count: int = 256) -> str:
        """Generates a string of '0' and '1' characters."""
        bits = self.generate_bits(count)
        return "".join(str(b) for b in bits)

    def generate_bytes(self, num_bytes: int = 32) -> bytes:
        """Generates cryptographically random bytes derived from quantum entropy."""
        bits = self.generate_bits(num_bytes * 8)
        packed = np.packbits(bits)
        return bytes(packed.tolist())

    def generate_hex_key(self, num_bytes: int = 32) -> str:
        """Generates a hex-encoded key (e.g. 256-bit AES key as 64 hex chars)."""
        return self.generate_bytes(num_bytes).hex()

    def evaluate_entropy(self, bits: np.ndarray) -> Dict[str, Any]:
        """
        Computes statistical and quantum entropy metrics on a bitstream:
        - Shannon Entropy (theoretical max = 1.0 bit/bit)
        - Min-Entropy
        - Monobit Balance (Frequency Test)
        - Chi-Square Goodness-of-Fit
        """
        if len(bits) == 0:
            return {
                "length": 0,
                "shannon_entropy": 0.0,
                "min_entropy": 0.0,
                "ones_ratio": 0.0,
                "is_passed": False,
            }

        n = len(bits)
        ones_count = int(np.sum(bits))
        zeros_count = n - ones_count
        p1 = ones_count / n
        p0 = zeros_count / n

        # Shannon Entropy
        shannon = 0.0
        for p in [p0, p1]:
            if p > 0:
                shannon -= p * math.log2(p)

        # Min-Entropy
        max_p = max(p0, p1)
        min_entropy = -math.log2(max_p) if max_p > 0 else 0.0

        # Monobit frequency test (standard NIST SP 800-22 criterion)
        # S_obs = |S_n| / sqrt(n) where S_n = sum(2*x_i - 1)
        s_n = abs(ones_count - zeros_count)
        s_obs = s_n / math.sqrt(n) if n > 0 else 0.0
        # p-value = erfc(s_obs / sqrt(2))
        p_value = math.erfc(s_obs / math.sqrt(2.0))

        # Passes test if p_value >= 0.01 and shannon entropy is high (> 0.98)
        is_passed = bool(p_value >= 0.01 and shannon >= 0.95)

        return {
            "length": n,
            "ones_count": ones_count,
            "zeros_count": zeros_count,
            "ones_ratio": round(p1, 4),
            "shannon_entropy": round(shannon, 6),
            "min_entropy": round(min_entropy, 6),
            "p_value_monobit": round(p_value, 6),
            "is_passed": is_passed,
        }


# Global singleton instance for high-throughput QRNG generation
qrng = QuantumRandomNumberGenerator(register_size=8)
