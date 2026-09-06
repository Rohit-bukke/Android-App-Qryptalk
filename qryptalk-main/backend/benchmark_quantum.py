"""
Performance Benchmark & Simulation Showcase for QrypTalk Quantum & QML Subsystems.
Measures QRNG generation throughput, QML classification inference latency, and BB84 key distillation speed.
"""

import time
import numpy as np

from app.core.quantum.qrng import qrng
from app.core.quantum.qml_model import qml_classifier
from app.core.quantum.bb84 import generate_bb84_key


def benchmark():
    print("=" * 70)
    print("        QRYPTALK QUANTUM & QML ENGINE BENCHMARK REPORT")
    print("=" * 70)

    # 1. Benchmark QRNG
    print("\n[1] Benchmarking Quantum Random Number Generator (QRNG)...")
    bit_counts = [1024, 4096, 16384]
    for count in bit_counts:
        t0 = time.perf_counter()
        bits = qrng.generate_bits(count)
        elapsed = (time.perf_counter() - t0) * 1000
        entropy = qrng.evaluate_entropy(bits)
        rate = (count / (elapsed / 1000.0)) / 1000.0  # kbits/sec
        print(f"  - {count:5d} bits generated in {elapsed:6.2f} ms | Throughput: {rate:7.2f} kbits/s | Shannon Entropy: {entropy['shannon_entropy']:.5f} (Pass: {entropy['is_passed']})")

    # 2. Benchmark QML Inference
    print("\n[2] Benchmarking Variational Quantum Classifier (QML Inference)...")
    iterations = 200
    test_cases = [
        ("Pristine Channel", 0.01, 0.50),
        ("Noisy Channel", 0.09, 0.49),
        ("Active Eavesdropper (Eve)", 0.25, 0.48),
        ("Critical Compromise", 0.42, 0.40),
    ]

    for label, qber, sift_ratio in test_cases:
        t0 = time.perf_counter()
        for _ in range(iterations):
            res = qml_classifier.classify_channel(qber=qber, sift_ratio=sift_ratio)
        avg_latency = ((time.perf_counter() - t0) / iterations) * 1000.0
        print(f"  - [{label:26s}] QBER: {qber:4.2f} -> Class: {res['predicted_class']:20s} | Conf: {res['confidence']:5.2%} | Avg Latency: {avg_latency:5.3f} ms")

    # 3. Benchmark Full BB84 Protocol
    print("\n[3] Benchmarking End-to-End BB84 Protocol (QRNG + QML + AES-256)...")
    for eve_flag in [False, True]:
        scenario = "Eavesdropper ACTIVE" if eve_flag else "Secure Channel (No Eve)"
        t0 = time.perf_counter()
        key, qber, status, telemetry = generate_bb84_key(n_bits=512, eve_enabled=eve_flag)
        elapsed = (time.perf_counter() - t0) * 1000.0
        print(f"  - Scenario: {scenario}")
        print(f"    Key Generated: {bool(key is not None)} | QBER: {qber:.2%} | QML State: {telemetry['predicted_class']}")
        print(f"    Elapsed Time: {elapsed:.2f} ms")
        if key:
            print(f"    AES-256 Key Digest: {key[:16]}...{key[-16:]}")

    print("\n" + "=" * 70)
    print("                 BENCHMARK COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    benchmark()
   