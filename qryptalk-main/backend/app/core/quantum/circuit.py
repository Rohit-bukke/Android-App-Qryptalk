"""
Quantum Circuit & Statevector Simulator for QrypTalk.
Provides high-performance, vectorized quantum state simulation, gate operations,
unitary transformations, projective measurements, and Pauli expectation values.
"""

from typing import List, Tuple, Union, Optional
import numpy as np


class QuantumCircuit:
    """
    Simulates an N-qubit quantum circuit using exact statevector propagation.
    Optimized with vectorized NumPy operations for low latency and high fidelity.
    """

    def __init__(self, num_qubits: int):
        if num_qubits < 1:
            raise ValueError("Circuit must have at least 1 qubit.")
        self.num_qubits = num_qubits
        self.dim = 1 << num_qubits
        # Initialize statevector to ground state |0...0>
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[0] = 1.0 + 0.0j
        self.gate_history: List[str] = []

    def reset(self):
        """Resets the circuit to the ground state |0...0>."""
        self.state.fill(0.0)
        self.state[0] = 1.0 + 0.0j
        self.gate_history.clear()

    def _apply_single_qubit_gate(self, gate_matrix: np.ndarray, target_qubit: int):
        """
        Applies a 2x2 unitary matrix to the target qubit using tensor reshapes.
        Target qubit index: 0 is the least significant qubit (rightmost).
        """
        n = self.num_qubits
        k = target_qubit
        shape = (1 << (n - k - 1), 2, 1 << k)
        state_tensor = self.state.reshape(shape)

        new_tensor = np.einsum("ab,ibk->iak", gate_matrix, state_tensor)
        self.state = new_tensor.reshape(self.dim)

    def h(self, qubit: int) -> "QuantumCircuit":
        """Applies Hadamard gate (creates equal superposition)."""
        h_matrix = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128) / np.sqrt(2.0)
        self._apply_single_qubit_gate(h_matrix, qubit)
        self.gate_history.append(f"H(q{qubit})")
        return self

    def x(self, qubit: int) -> "QuantumCircuit":
        """Applies Pauli-X (Bit-flip / NOT) gate."""
        x_matrix = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
        self._apply_single_qubit_gate(x_matrix, qubit)
        self.gate_history.append(f"X(q{qubit})")
        return self

    def y(self, qubit: int) -> "QuantumCircuit":
        """Applies Pauli-Y gate."""
        y_matrix = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
        self._apply_single_qubit_gate(y_matrix, qubit)
        self.gate_history.append(f"Y(q{qubit})")
        return self

    def z(self, qubit: int) -> "QuantumCircuit":
        """Applies Pauli-Z (Phase-flip) gate."""
        z_matrix = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
        self._apply_single_qubit_gate(z_matrix, qubit)
        self.gate_history.append(f"Z(q{qubit})")
        return self

    def rx(self, theta: float, qubit: int) -> "QuantumCircuit":
        """Applies single-qubit X-rotation: Rx(theta) = exp(-i * theta/2 * X)."""
        cos_half = np.cos(theta / 2.0)
        sin_half = np.sin(theta / 2.0)
        rx_matrix = np.array(
            [[cos_half, -1j * sin_half], [-1j * sin_half, cos_half]],
            dtype=np.complex128,
        )
        self._apply_single_qubit_gate(rx_matrix, qubit)
        self.gate_history.append(f"Rx({theta:.3f}, q{qubit})")
        return self

    def ry(self, theta: float, qubit: int) -> "QuantumCircuit":
        """Applies single-qubit Y-rotation: Ry(theta) = exp(-i * theta/2 * Y)."""
        cos_half = np.cos(theta / 2.0)
        sin_half = np.sin(theta / 2.0)
        ry_matrix = np.array(
            [[cos_half, -sin_half], [sin_half, cos_half]],
            dtype=np.complex128,
        )
        self._apply_single_qubit_gate(ry_matrix, qubit)
        self.gate_history.append(f"Ry({theta:.3f}, q{qubit})")
        return self

    def rz(self, theta: float, qubit: int) -> "QuantumCircuit":
        """Applies single-qubit Z-rotation: Rz(theta) = exp(-i * theta/2 * Z)."""
        rz_matrix = np.array(
            [[np.exp(-1j * theta / 2.0), 0.0], [0.0, np.exp(1j * theta / 2.0)]],
            dtype=np.complex128,
        )
        self._apply_single_qubit_gate(rz_matrix, qubit)
        self.gate_history.append(f"Rz({theta:.3f}, q{qubit})")
        return self

    def cnot(self, control: int, target: int) -> "QuantumCircuit":
        """Applies Controlled-NOT (CX) entangling gate."""
        if control == target:
            raise ValueError("Control and target qubits cannot be identical.")

        n = self.num_qubits
        shape = [2] * n
        state_tensor = self.state.reshape(shape)

        slices_0 = [slice(None)] * n
        slices_1 = [slice(None)] * n

        slices_0[n - 1 - control] = 1
        slices_0[n - 1 - target] = 0

        slices_1[n - 1 - control] = 1
        slices_1[n - 1 - target] = 1

        temp = state_tensor[tuple(slices_0)].copy()
        state_tensor[tuple(slices_0)] = state_tensor[tuple(slices_1)]
        state_tensor[tuple(slices_1)] = temp

        self.state = state_tensor.reshape(self.dim)
        self.gate_history.append(f"CNOT(q{control} -> q{target})")
        return self

    def cz(self, control: int, target: int) -> "QuantumCircuit":
        """Applies Controlled-Z entangling gate."""
        if control == target:
            raise ValueError("Control and target qubits cannot be identical.")

        n = self.num_qubits
        shape = [2] * n
        state_tensor = self.state.reshape(shape)

        slices = [slice(None)] * n
        slices[n - 1 - control] = 1
        slices[n - 1 - target] = 1

        state_tensor[tuple(slices)] *= -1.0
        self.state = state_tensor.reshape(self.dim)
        self.gate_history.append(f"CZ(q{control} -> q{target})")
        return self

    def get_probabilities(self) -> np.ndarray:
        """Returns the measurement probability distribution |c_i|^2 across all 2^N states."""
        probs = np.abs(self.state) ** 2
        total = np.sum(probs)
        if total > 0:
            probs /= total
        return probs

    def measure_all(self, shots: int = 1) -> np.ndarray:
        """
        Samples measurements from the quantum state probability distribution.
        Returns an array of measured integer states [0, 2^N - 1].
        """
        probs = self.get_probabilities()
        outcomes = np.random.choice(self.dim, size=shots, p=probs)
        return outcomes

    def expectation_z(self, qubit: int) -> float:
        """
        Computes the analytical expectation value <Z> for a specific qubit:
        <Z> = P(qubit = 0) - P(qubit = 1) in [-1.0, 1.0].
        """
        probs = self.get_probabilities()
        n = self.num_qubits
        indices = np.arange(self.dim)
        bit_is_one = (indices >> qubit) & 1
        p1 = np.sum(probs[bit_is_one == 1])
        p0 = 1.0 - p1
        return float(p0 - p1)

    def expectation_all_z(self) -> List[float]:
        """Computes expectation values [<Z_0>, <Z_1>, ..., <Z_{N-1}>]."""
        return [self.expectation_z(q) for q in range(self.num_qubits)]

    def get_shannon_entropy(self) -> float:
        """Computes the Shannon entropy (in bits) of the measurement distribution."""
        probs = self.get_probabilities()
        nonzero_probs = probs[probs > 1e-15]
        return float(-np.sum(nonzero_probs * np.log2(nonzero_probs)))
