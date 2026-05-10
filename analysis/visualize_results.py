"""
Analysis & Visualization
========================
Generates publication-quality figures from experiment results.
Run AFTER bell_state_experiment.py has produced results/experiment_results.json
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os

os.makedirs("results/figures", exist_ok=True)

# ── Load results ───────────────────────────────────────────────────────────────
with open("results/experiment_results.json", "r") as f:
    data = json.load(f)

QUANTUM_BOUND = data["quantum_chsh_bound"]   # 2√2 ≈ 2.828
CLASSICAL_BOUND = data["classical_chsh_bound"]  # 2.0

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "figure.dpi": 150,
})


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Measurement Outcome Distributions (Ideal vs Noisy)
# ══════════════════════════════════════════════════════════════════════════════

def plot_outcome_distributions():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.suptitle("Figure 1: Bell State Measurement Outcomes", fontsize=14, fontweight="bold")

    ideal = data["ideal_counts"]
    noisy = data["noisy_counts"]
    all_states = sorted(set(list(ideal.keys()) + list(noisy.keys())))

    colors = {"00": "#2563EB", "11": "#16A34A", "01": "#DC2626", "10": "#D97706"}

    for ax, counts, title in zip(axes, [ideal, noisy], ["Ideal Simulator", "Noisy Simulator (p=0.01)"]):
        total = sum(counts.values())
        states = all_states
        probs = [counts.get(s, 0) / total for s in states]
        bar_colors = [colors.get(s, "#6B7280") for s in states]

        bars = ax.bar(states, probs, color=bar_colors, edgecolor="white", linewidth=1.5, width=0.5)
        ax.set_ylim(0, 1)
        ax.set_ylabel("Probability")
        ax.set_xlabel("Measurement Outcome")
        ax.set_title(title)
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.6, label="Ideal (50%)")
        ax.legend(fontsize=9)

        # Annotate bars
        for bar, prob in zip(bars, probs):
            if prob > 0.01:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f"{prob:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("results/figures/fig1_outcome_distributions.png", bbox_inches="tight")
    plt.close()
    print("✓ Saved Figure 1: Outcome Distributions")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: CHSH Inequality — Visualizing the Violation
# ══════════════════════════════════════════════════════════════════════════════

def plot_chsh_violation():
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle("Figure 2: CHSH Inequality Violation", fontsize=14, fontweight="bold")

    S_ideal = abs(data["chsh_ideal"]["S"])
    S_noisy = abs(data["chsh_noisy"]["S"])

    labels = ["Classical\nBound", "Noisy\nSimulator", "Ideal\nSimulator", "Quantum\nBound"]
    values = [CLASSICAL_BOUND, S_noisy, S_ideal, QUANTUM_BOUND]
    colors = ["#6B7280", "#F59E0B", "#2563EB", "#059669"]
    alphas = [0.6, 0.85, 0.85, 0.6]

    bars = ax.bar(labels, values, color=colors, alpha=0.85, edgecolor="white",
                  linewidth=1.5, width=0.55)

    # Reference lines
    ax.axhline(CLASSICAL_BOUND, color="#6B7280", linestyle="--", linewidth=1.2,
               label=f"Classical bound |S| = {CLASSICAL_BOUND}")
    ax.axhline(QUANTUM_BOUND, color="#059669", linestyle="--", linewidth=1.2,
               label=f"Quantum bound |S| = 2√2 ≈ {QUANTUM_BOUND:.3f}")

    # Shade violation zone
    ax.axhspan(CLASSICAL_BOUND, QUANTUM_BOUND + 0.15, alpha=0.06, color="#2563EB",
               label="Quantum violation zone")

    # Annotate bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"|S| = {val:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylabel("|S| — CHSH Parameter")
    ax.set_ylim(0, QUANTUM_BOUND + 0.4)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("Measuring Bell's inequality violation proves quantum entanglement", fontsize=11, style="italic")

    plt.tight_layout()
    plt.savefig("results/figures/fig2_chsh_violation.png", bbox_inches="tight")
    plt.close()
    print("✓ Saved Figure 2: CHSH Violation")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3: Fidelity & CHSH vs Noise Level (Main Research Finding)
# ══════════════════════════════════════════════════════════════════════════════

def plot_noise_sweep():
    fig, ax1 = plt.subplots(figsize=(9, 5))
    fig.suptitle("Figure 3: Entanglement Degradation Under Depolarizing Noise", 
                 fontsize=14, fontweight="bold")

    sweep = data["noise_sweep"]
    p_vals = [r["p_depol"] for r in sweep]
    fidelities = [r["fidelity"] for r in sweep]
    chsh_vals = [r["chsh_S"] for r in sweep]

    # Fidelity (left axis)
    color1 = "#2563EB"
    ax1.set_xlabel("Depolarizing Error Rate (p)")
    ax1.set_ylabel("State Fidelity F", color=color1)
    l1, = ax1.plot(p_vals, fidelities, "o-", color=color1, linewidth=2,
                   markersize=7, label="Fidelity F")
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(0, 1.05)
    ax1.axhline(1.0, color=color1, linestyle=":", alpha=0.4)

    # CHSH S (right axis)
    ax2 = ax1.twinx()
    color2 = "#DC2626"
    ax2.set_ylabel("|S| — CHSH Parameter", color=color2)
    l2, = ax2.plot(p_vals, chsh_vals, "s--", color=color2, linewidth=2,
                   markersize=7, label="|S| CHSH")
    ax2.axhline(CLASSICAL_BOUND, color="#6B7280", linestyle="--", linewidth=1,
                label=f"Classical bound = {CLASSICAL_BOUND}")
    ax2.axhline(QUANTUM_BOUND, color="#059669", linestyle=":", linewidth=1,
                label=f"Quantum bound = {QUANTUM_BOUND:.3f}")
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(1.5, 3.1)

    # Shade entanglement-preserved vs destroyed regions
    classical_breach = next((r["p_depol"] for r in sweep if not r["entangled"]), None)
    if classical_breach:
        ax1.axvspan(classical_breach, max(p_vals), alpha=0.07, color="#DC2626",
                    label="Entanglement lost")

    # Combined legend
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="lower left", fontsize=9)
    ax2.legend(loc="upper right", fontsize=9)

    ax1.set_xscale("log")
    plt.tight_layout()
    plt.savefig("results/figures/fig3_noise_sweep.png", bbox_inches="tight")
    plt.close()
    print("✓ Saved Figure 3: Noise Sweep")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Summary Dashboard
# ══════════════════════════════════════════════════════════════════════════════

def plot_summary_dashboard():
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle("Bell-State Entanglement Research — Summary Dashboard\nGeorge Oppong Boateng, KNUST EEE | Quantum Computing Research",
                 fontsize=13, fontweight="bold")
    gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.4)

    # Panel A: Outcome counts ideal
    ax_a = fig.add_subplot(gs[0, 0])
    ideal = data["ideal_counts"]
    total = sum(ideal.values())
    states = sorted(ideal.keys())
    probs = [ideal.get(s, 0)/total for s in states]
    ax_a.bar(states, probs, color=["#2563EB", "#16A34A"], edgecolor="white")
    ax_a.set_title("A. Ideal Outcome")
    ax_a.set_ylabel("Probability")
    ax_a.set_ylim(0, 1)

    # Panel B: Outcome counts noisy
    ax_b = fig.add_subplot(gs[0, 1])
    noisy = data["noisy_counts"]
    total_n = sum(noisy.values())
    all_s = sorted(set(list(ideal.keys()) + list(noisy.keys())))
    p_noisy = [noisy.get(s, 0)/total_n for s in all_s]
    colors_b = ["#2563EB", "#DC2626", "#D97706", "#16A34A"]
    ax_b.bar(all_s, p_noisy, color=colors_b[:len(all_s)], edgecolor="white")
    ax_b.set_title("B. Noisy Outcome (p=0.01)")
    ax_b.set_ylim(0, 1)

    # Panel C: CHSH comparison
    ax_c = fig.add_subplot(gs[0, 2])
    S_ideal = abs(data["chsh_ideal"]["S"])
    S_noisy = abs(data["chsh_noisy"]["S"])
    ax_c.barh(["Ideal", "Noisy"], [S_ideal, S_noisy],
              color=["#2563EB", "#F59E0B"], edgecolor="white")
    ax_c.axvline(CLASSICAL_BOUND, color="red", linestyle="--", label="Classical limit")
    ax_c.axvline(QUANTUM_BOUND, color="green", linestyle=":", label="Quantum max")
    ax_c.set_title("C. CHSH |S| Values")
    ax_c.set_xlim(0, 3.2)
    ax_c.legend(fontsize=7)

    # Panel D: Noise sweep (spans bottom row)
    ax_d = fig.add_subplot(gs[1, :])
    sweep = data["noise_sweep"]
    p_vals = [r["p_depol"] for r in sweep]
    fidelities = [r["fidelity"] for r in sweep]
    chsh_s = [r["chsh_S"] for r in sweep]

    ax_d.plot(p_vals, fidelities, "o-", color="#2563EB", label="Fidelity F", linewidth=2, markersize=7)
    ax_d2 = ax_d.twinx()
    ax_d2.plot(p_vals, chsh_s, "s--", color="#DC2626", label="|S| CHSH", linewidth=2, markersize=7)
    ax_d2.axhline(CLASSICAL_BOUND, color="gray", linestyle=":", linewidth=1)
    ax_d.set_xscale("log")
    ax_d.set_title("D. Fidelity & CHSH vs Noise Level")
    ax_d.set_xlabel("Depolarizing Error Rate (p)")
    ax_d.set_ylabel("Fidelity", color="#2563EB")
    ax_d2.set_ylabel("|S|", color="#DC2626")
    ax_d.legend(loc="lower left", fontsize=9)
    ax_d2.legend(loc="lower right", fontsize=9)

    plt.savefig("results/figures/fig4_summary_dashboard.png", bbox_inches="tight", dpi=150)
    plt.close()
    print("✓ Saved Figure 4: Summary Dashboard")


# ══════════════════════════════════════════════════════════════════════════════
# RUN ALL
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n── Generating Research Figures ──\n")
    plot_outcome_distributions()
    plot_chsh_violation()
    plot_noise_sweep()
    plot_summary_dashboard()
    print("\n✓ All figures saved to results/figures/")
