"""
Quantum Key Distribution (BB84 Protocol) Engine with QRNG & QML Threat Intelligence.
Orchestrates quantum bit generation, polarization basis encoding, channel transmission,
sifting, QBER calculation, and real-time Variational Quantum Machine Learning (QML) security classification.
"""

from typing import Tuple, Optional, Dict, Any
import numpy as np
import hashlib

from app.core.quantum.qrng import qrng
from app.core.quantum.qml_model import qml_classifier


def generate_bb84_key(
    n_bits: int = 256,
    eve_enabled: bool = False,
    qber_sample_size: float = 0.5,
) -> Tuple[Optional[str], float, str, Dict[str, Any]]:
    """
    Executes the BB84 QKD protocol enhanced with:
    1. Quantum Random Number Generator (QRNG) for non-deterministic bit & basis generation.
    2. Variational Quantum Machine Learning (QML) for real-time channel threat classification.
    3. Dynamic privacy amplification and 256-bit SHA-256/AES-GCM key distillation.

    :param n_bits: Total quantum bits exchanged over the quantum channel.
    :param eve_enabled: Whether an active intercept-resend eavesdropper (Eve) is present.
    :param qber_sample_size: Fraction of sifted bits used for public error parameter estimation.
    :return: (hex_key, qber, status_message, qml_telemetry)
    """
    # 1. Step 1: Quantum Entropy Generation via QRNG
    # Alice generates raw bits and basis choices using quantum superposition collapse
    alice_bits = qrng.generate_bits(n_bits)
    alice_bases = qrng.generate_bits(n_bits)  # 0: Z-basis (|0>, |1>), 1: X-basis (|+>, |->)

    # Bob chooses his measurement bases using QRNG
    bob_bases = qrng.generate_bits(n_bits)
    bob_results = np.zeros(n_bits, dtype=int)

    # 2. Step 2: Quantum Channel Simulation & Interception
    for i in range(n_bits):
        qubit = int(alice_bits[i])

        # Eve Interception (Intercept-Resend Attack)
        if eve_enabled:
            eve_basis = int(qrng.generate_bits(1)[0])
            if alice_bases[i] != eve_basis:
                # 50% chance of introducing quantum state perturbation
                if qrng.generate_bits(1)[0] == 1:
                    qubit = 1 - qubit

        # Bob Measurement
        if alice_bases[i] != bob_bases[i]:
            # Measurement in non-conjugate basis yields random 50/50 outcome
            bob_results[i] = int(qrng.generate_bits(1)[0])
        else:
            # Conjugate basis preserves state in noiseless channel
            bob_results[i] = qubit

    # 3. Step 3: Classical Basis Sifting
    sifted_indices = np.where(alice_bases == bob_bases)[0]
    total_sifted = len(sifted_indices)

    if total_sifted < 20:
        telemetry = qml_classifier.classify_channel(qber=1.0, sift_ratio=total_sifted / n_bits)
        return None, 1.0, "Key generation aborted: insufficient matching bases.", telemetry

    # 4. Step 4: QBER Estimation & Error Asymmetry
    sample_count = max(1, int(total_sifted * qber_sample_size))
    if sample_count >= total_sifted:
        sample_count = total_sifted // 2

    # Sample random sifted indices for public parameter estimation
    sampled_indices = np.random.choice(sifted_indices, size=sample_count, replace=False)
    mismatches = int(np.sum(alice_bits[sampled_indices] != bob_results[sampled_indices]))
    qber = mismatches / sample_count if sample_count > 0 else 0.0

    # Compute error asymmetry between X and Z bases
    z_mask = (alice_bases[sampled_indices] == 0)
    x_mask = (alice_bases[sampled_indices] == 1)
    z_err = np.mean(alice_bits[sampled_indices[z_mask]] != bob_results[sampled_indices[z_mask]]) if np.any(z_mask) else 0.0
    x_err = np.mean(alice_bits[sampled_indices[x_mask]] != bob_results[sampled_indices[x_mask]]) if np.any(x_mask) else 0.0
    error_asymmetry = float(x_err - z_err)

    # Basis entropy
    bases_entropy_data = qrng.evaluate_entropy(alice_bases)
    basis_entropy = bases_entropy_data.get("shannon_entropy", 1.0)

    # 5. Step 5: Real-Time QML Channel Threat Classification
    sift_ratio = float(total_sifted / n_bits)
    qml_telemetry = qml_classifier.classify_channel(
        qber=qber,
        sift_ratio=sift_ratio,
        basis_entropy=basis_entropy,
        error_asymmetry=error_asymmetry,
    )

    # 6. Step 6: Security Verification & Privacy Amplification
    security_threshold = 0.15
    if not qml_telemetry["is_secure"] or qber > security_threshold:
        return (
            None,
            qber,
            f"Security Alert: {qml_telemetry['predicted_class']} detected (QBER={qber:.2%}). Key exchange aborted.",
            qml_telemetry,
        )

    # 7. Step 7: Final Shared Secret Key Distillation
    remaining_indices = np.setdiff1d(sifted_indices, sampled_indices)
    raw_key_bits = "".join(str(alice_bits[i]) for i in remaining_indices)

    # Distill into a 256-bit cryptographic AES key via SHA-256 hash function (Privacy Amplification)
    derived_aes_key = hashlib.sha256(raw_key_bits.encode("utf-8")).hexdigest()

    status_message = (
        f"Key Secure ({len(raw_key_bits)} sifted bits distilled to 256-bit AES). "
        f"QBER: {qber:.2%} | QML State: {qml_telemetry['predicted_class']}"
    )

    return derived_aes_key, qber, status_message, qml_telemetry
