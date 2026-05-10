"""
Bell-State Entanglement Fidelity Under Noise
============================================
Research Project — George Oppong Boateng, KNUST EEE 
Characterizing Bell-state entanglement using IBM Qiskit:
  1. Ideal simulator (baseline)
  2. Noisy simulator (fake backend)
  3. CHSH inequality violation measurement
  4. State fidelity calculation
"""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error
from qiskit.quantum_info import state_fidelity, Statevector, DensityMatrix
import numpy as np
import json
import os

# ─── Output directory ─────────────────────────────────────────────────────────
os.makedirs("results", exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# 1. BUILD BELL STATE CIRCUIT
# ══════════════════════════════════════════════════════════════════════════════

def build_bell_circuit():
    """Create the Φ+ Bell state: |Φ+⟩ = (|00⟩ + |11⟩) / √2"""
    qc = QuantumCircuit(2, 2)
    qc.h(0)          # Hadamard on qubit 0 → superposition
    qc.cx(0, 1)      # CNOT: entangles qubit 0 and qubit 1
    return qc


def build_bell_circuit_with_measurement():
    """Bell circuit with standard Z-basis measurement."""
    qc = build_bell_circuit()
    qc.measure([0, 1], [0, 1])
    return qc


# ══════════════════════════════════════════════════════════════════════════════
# 2. IDEAL SIMULATOR RUN
# ══════════════════════════════════════════════════════════════════════════════

def run_ideal(shots=4096):
    """Run Bell state on perfect (noiseless) AerSimulator."""
    qc = build_bell_circuit_with_measurement()
    simulator = AerSimulator()
    job = simulator.run(transpile(qc, simulator), shots=shots)
    result = job.result()
    counts = result.get_counts()
    print(f"[Ideal] Counts: {counts}")
    return counts


# ══════════════════════════════════════════════════════════════════════════════
# 3. NOISY SIMULATOR RUN
# ══════════════════════════════════════════════════════════════════════════════

def build_noise_model(p_depol=0.01, t1=50e3, t2=70e3, gate_time=100):
    """
    Construct a realistic noise model:
      - Depolarizing error on single-qubit gates
      - Thermal relaxation (T1/T2 decoherence) on 2-qubit gates
    Parameters match approximate IBM Eagle processor specs.
    """
    noise_model = NoiseModel()

    # Single-qubit depolarizing error (e.g. X, H gates)
    dep_error_1q = depolarizing_error(p_depol, 1)
    noise_model.add_all_qubit_quantum_error(dep_error_1q, ['h', 'x', 'u1', 'u2', 'u3'])

    # 2-qubit depolarizing error (CNOT)
    dep_error_2q = depolarizing_error(p_depol * 10, 2)
    noise_model.add_all_qubit_quantum_error(dep_error_2q, ['cx'])

    # Thermal relaxation on measurement
    therm_error = thermal_relaxation_error(t1, t2, gate_time)
    noise_model.add_all_qubit_quantum_error(therm_error, ['measure'])

    return noise_model


def run_noisy(shots=4096, p_depol=0.01):
    """Run Bell state on noisy simulator."""
    qc = build_bell_circuit_with_measurement()
    noise_model = build_noise_model(p_depol=p_depol)
    simulator = AerSimulator(noise_model=noise_model)
    job = simulator.run(transpile(qc, simulator), shots=shots)
    result = job.result()
    counts = result.get_counts()
    print(f"[Noisy p={p_depol}] Counts: {counts}")
    return counts


# ══════════════════════════════════════════════════════════════════════════════
# 4. STATE FIDELITY CALCULATION
# ══════════════════════════════════════════════════════════════════════════════

def compute_fidelity(noise_level=0.01):
    """
    Calculate fidelity between ideal Bell state and noisy density matrix.
    Fidelity = 1.0 means perfect entanglement, 0.0 means completely mixed.
    """
    # Ideal Bell state vector
    ideal_statevector = Statevector.from_label('00')
    qc = build_bell_circuit()
    ideal_state = ideal_statevector.evolve(qc)

    # Noisy density matrix via simulation
    noise_model = build_noise_model(p_depol=noise_level)
    simulator = AerSimulator(noise_model=noise_model, method='density_matrix')
    qc_no_meas = build_bell_circuit()
    qc_no_meas.save_density_matrix()
    job = simulator.run(transpile(qc_no_meas, simulator))
    result = job.result()
    noisy_dm = DensityMatrix(result.data()['density_matrix'])

    fidelity = state_fidelity(ideal_state, noisy_dm)
    print(f"[Fidelity] p_depol={noise_level:.4f} → F = {fidelity:.4f}")
    return fidelity


# ══════════════════════════════════════════════════════════════════════════════
# 5. CHSH INEQUALITY VIOLATION
# ══════════════════════════════════════════════════════════════════════════════
# The CHSH inequality states that for any local hidden variable theory: |S| ≤ 2
# Quantum mechanics predicts: |S| = 2√2 ≈ 2.828
# Measuring S > 2 PROVES entanglement (Bell's theorem).

def chsh_circuit(theta_a, theta_b):
    """
    Bell state circuit with rotated measurement bases.
    Alice measures at angle theta_a, Bob at theta_b.
    """
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    # Rotate measurement basis
    qc.ry(-2 * theta_a, 0)
    qc.ry(-2 * theta_b, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def get_expectation(counts, shots):
    """
    Compute <AB> correlation from measurement counts.
    +1 for same outcomes (00, 11), -1 for different (01, 10).
    """
    same = counts.get('00', 0) + counts.get('11', 0)
    diff = counts.get('01', 0) + counts.get('10', 0)
    return (same - diff) / shots


def compute_chsh(shots=8192, noisy=False, p_depol=0.01):
    """
    Measure CHSH parameter S using 4 angle combinations.
    Optimal angles for max violation: a=0, a'=π/4, b=π/8, b'=3π/8
    S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
    """
    a  = 0
    a2 = np.pi / 4
    b  = np.pi / 8
    b2 = 3 * np.pi / 8

    angle_pairs = [(a, b), (a, b2), (a2, b), (a2, b2)]
    correlations = []

    if noisy:
        noise_model = build_noise_model(p_depol=p_depol)
        simulator = AerSimulator(noise_model=noise_model)
    else:
        simulator = AerSimulator()

    for theta_a, theta_b in angle_pairs:
        qc = chsh_circuit(theta_a, theta_b)
        job = simulator.run(transpile(qc, simulator), shots=shots)
        counts = job.result().get_counts()
        E = get_expectation(counts, shots)
        correlations.append(E)

    E_ab, E_ab2, E_a2b, E_a2b2 = correlations
    S = E_ab - E_ab2 + E_a2b + E_a2b2

    label = "Noisy" if noisy else "Ideal"
    print(f"[CHSH {label}] S = {S:.4f}  (quantum max = {2*np.sqrt(2):.4f}, classical bound = 2.0000)")
    return S, correlations


# ══════════════════════════════════════════════════════════════════════════════
# 6. NOISE SWEEP — Fidelity vs Depolarizing Error Rate
# ══════════════════════════════════════════════════════════════════════════════

def noise_sweep():
    """Sweep depolarizing error from 0.001 to 0.1, record fidelity and CHSH S."""
    noise_levels = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
    results = []

    for p in noise_levels:
        fidelity = compute_fidelity(noise_level=p)
        S, _ = compute_chsh(noisy=True, p_depol=p, shots=4096)
        results.append({
            "p_depol": p,
            "fidelity": round(fidelity, 4),
            "chsh_S": round(float(S), 4),
            "entangled": abs(S) > 2.0
        })

    return results


# ══════════════════════════════════════════════════════════════════════════════
# 7. MAIN — Run all experiments and save results
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  BELL STATE ENTANGLEMENT RESEARCH — George Oppong Boateng, KNUST")
    print("="*60 + "\n")

    # Step 1: Ideal run
    print("── Step 1: Ideal Simulation ──")
    ideal_counts = run_ideal(shots=4096)

    # Step 2: Noisy run
    print("\n── Step 2: Noisy Simulation ──")
    noisy_counts = run_noisy(shots=4096, p_depol=0.01)

    # Step 3: CHSH ideal
    print("\n── Step 3: CHSH Inequality (Ideal) ──")
    S_ideal, corr_ideal = compute_chsh(shots=8192, noisy=False)

    # Step 4: CHSH noisy
    print("\n── Step 4: CHSH Inequality (Noisy) ──")
    S_noisy, corr_noisy = compute_chsh(shots=8192, noisy=True, p_depol=0.01)

    # Step 5: Fidelity at standard noise level
    print("\n── Step 5: State Fidelity ──")
    fidelity = compute_fidelity(noise_level=0.01)

    # Step 6: Noise sweep
    print("\n── Step 6: Noise Sweep ──")
    sweep_results = noise_sweep()

    # Save all results to JSON for analysis/plotting
    output = {
        "ideal_counts": ideal_counts,
        "noisy_counts": noisy_counts,
        "chsh_ideal": {"S": float(S_ideal), "correlations": [float(c) for c in corr_ideal]},
        "chsh_noisy": {"S": float(S_noisy), "correlations": [float(c) for c in corr_noisy]},
        "fidelity_at_p001": float(fidelity),
        "noise_sweep": sweep_results,
        "quantum_chsh_bound": float(2 * np.sqrt(2)),
        "classical_chsh_bound": 2.0
    }

    with open("results/experiment_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\n✓ All results saved to results/experiment_results.json")
    print("\n" + "="*60)
    print(f"  CHSH Ideal:  S = {S_ideal:.4f}  {'✓ ENTANGLEMENT PROVEN' if abs(S_ideal) > 2 else '✗ No violation'}")
    print(f"  CHSH Noisy:  S = {S_noisy:.4f}  {'✓ Still entangled' if abs(S_noisy) > 2 else '✗ Noise destroyed entanglement'}")
    print(f"  Fidelity:    F = {fidelity:.4f}")
    print("="*60 + "\n")
