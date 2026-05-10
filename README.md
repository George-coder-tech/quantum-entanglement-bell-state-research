# Bell-State Entanglement Fidelity Under Noise
### Characterizing Quantum Entanglement on IBM Quantum Simulators

**Author:** George Oppong Boateng · KNUST, Electrical & Electronics Engineering (Year 2)  
**Tools:** Qiskit, Qiskit Aer, IBM Quantum  
**Status:** Active Research — Simulation Phase Complete | Hardware Runs Pending

---

## Abstract

This project investigates how depolarizing noise and thermal decoherence degrade Bell-state entanglement in near-term quantum hardware. Using IBM Qiskit, we construct the Φ⁺ Bell state, verify entanglement through CHSH inequality violation (achieving |S| ≈ 2.82 on an ideal simulator vs. the classical bound of 2.0), and quantify entanglement fidelity across a range of depolarizing error rates (p = 0.001 to 0.1). Results show a monotonic decrease in both fidelity and CHSH parameter as noise increases, with entanglement fully destroyed around p ≈ 0.05 under our noise model. Future work extends these experiments to real IBM Quantum hardware.

---

## Research Question

> *At what depolarizing error rate does Bell-state entanglement become undetectable, and how does state fidelity correlate with CHSH violation strength across realistic noise regimes?*

---

## Background

**Bell states** are maximally entangled two-qubit states — the simplest unit of quantum entanglement. The Φ⁺ state used here is:

$$|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

**Why this matters:** Bell states are the foundation of quantum teleportation, superdense coding, and quantum key distribution (QKD). Understanding how noise degrades them is critical for building reliable quantum networks and fault-tolerant quantum computers.

**The CHSH inequality** is a mathematical test that *proves* entanglement. Any local hidden variable (classical) theory must satisfy |S| ≤ 2. Quantum mechanics predicts |S| = 2√2 ≈ 2.828. Measuring |S| > 2 is a proof of entanglement — this is what we measure in this project.

---

## Methodology

### Circuit Construction
```
q0: ─[H]─●─ measure
          │
q1: ─────X─ measure
```
A Hadamard gate on qubit 0 creates superposition. The CNOT gate entangles qubit 1 with qubit 0, producing the Φ⁺ Bell state.

### Noise Model
We implement a physically motivated noise model with two components:
- **Depolarizing error** on single-qubit gates (rate p) and two-qubit gates (rate 10p)
- **Thermal relaxation** (T1 = 50μs, T2 = 70μs) on measurement, approximating IBM Eagle processor specs

### Experiments
| Experiment | Description |
|---|---|
| Ideal simulation | Noiseless AerSimulator baseline |
| Noisy simulation | Custom noise model (p = 0.01) |
| CHSH violation | 4 measurement angles, 8192 shots each |
| State fidelity | Density matrix vs ideal state vector |
| Noise sweep | p ∈ {0.001, 0.005, 0.01, 0.02, 0.05, 0.1} |

---

## Results

### Ideal Simulator
- Measurement outcomes: ~50% |00⟩, ~50% |11⟩ (expected for perfect Bell state)
- CHSH parameter: **|S| ≈ 2.82** ✓ Entanglement proven (exceeds classical bound of 2.0)
- State fidelity: **F ≈ 1.00**

### Noisy Simulator (p = 0.01)
- Small probability leakage into |01⟩ and |10⟩ states observed
- CHSH parameter: **|S| > 2.0** ✓ Entanglement still detectable
- State fidelity: **F ≈ 0.96**

### Noise Sweep Finding
Fidelity and CHSH parameter both degrade monotonically with increasing p. At p ≈ 0.05, the CHSH parameter approaches the classical bound — entanglement becomes undetectable under this noise model.

*(See figures in `results/figures/`)*

---

## Repository Structure

```
├── experiment/
│   └── bell_state_experiment.py   # Main experiment: circuits, CHSH, fidelity, noise sweep
├── analysis/
│   └── visualize_results.py       # Publication-quality figures
├── results/
│   ├── experiment_results.json    # Raw numerical results
│   └── figures/                   # Generated plots
│       ├── fig1_outcome_distributions.png
│       ├── fig2_chsh_violation.png
│       ├── fig3_noise_sweep.png
│       └── fig4_summary_dashboard.png
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the experiment (generates results/experiment_results.json)
python experiment/bell_state_experiment.py

# 3. Generate figures
python analysis/visualize_results.py
```

---

## Future Work

- [ ] Run circuits on **real IBM Quantum hardware** (ibm_brisbane or ibm_kyoto) and compare to simulation
- [ ] Extend to **all 4 Bell states** (Φ⁺, Φ⁻, Ψ⁺, Ψ⁻)
- [ ] Implement **quantum error mitigation** (Zero Noise Extrapolation) and measure improvement
- [ ] Scale to **GHZ states** (3-qubit entanglement) and study multipartite noise
- [ ] Compare noise mitigation strategies: ZNE vs Probabilistic Error Cancellation

---

## References

1. Bell, J.S. (1964). On the Einstein Podolsky Rosen Paradox. *Physics*, 1(3), 195–200.
2. Clauser, J.F., Horne, M.A., Shimony, A., Holt, R.A. (1969). Proposed experiment to test local hidden-variable theories. *PRL*, 23(15), 880.
3. Qiskit Contributors (2023). Qiskit: An Open-source Framework for Quantum Computing. DOI: 10.5281/zenodo.2573505
4. Nielsen, M.A., Chuang, I.L. (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.

---

## About

This project is part of my self-directed research in quantum computing during my undergraduate studies in Electrical & Electronics Engineering at KNUST, Ghana. I am building toward a PhD in quantum computing, with a focus on quantum error correction and near-term quantum hardware.

📧 Connect: [LinkedIn](#) | [Email](#)

