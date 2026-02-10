import numpy as np

def generate_bb84_key(n_bits=256, eve_enabled=False, qber_sample_size=0.5):

    alice_bits = np.random.randint(2, size=n_bits)
    alice_bases = np.random.randint(2, size=n_bits)
    bob_bases = np.random.randint(2, size=n_bits)

    bob_results = np.zeros(n_bits, dtype=int)

    for i in range(n_bits):
        qubit = alice_bits[i]

        if eve_enabled:
            eve_basis = np.random.randint(2)
            if alice_bases[i] != eve_basis:
                if np.random.random() < 0.5:
                    qubit = 1 - qubit

        if alice_bases[i] != bob_bases[i]:
            bob_results[i] = np.random.randint(2)
        else:
            bob_results[i] = qubit

    sifted = np.where(alice_bases == bob_bases)[0]

    if len(sifted) < 20:
        return None, 1.0, "Not enough matching bases"

    sample_size = int(len(sifted) * qber_sample_size)
    sample = np.random.choice(sifted, size=sample_size, replace=False)

    mismatches = sum(1 for i in sample if alice_bits[i] != bob_results[i])
    qber = mismatches / sample_size

    if qber > 0.15:
        return None, qber, "Eavesdropper detected"

    final_indices = np.setdiff1d(sifted, sample)
    key = "".join(str(alice_bits[i]) for i in final_indices)

    return key, qber, "Key secure"
