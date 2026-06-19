import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from pathlib import Path

def analyze_frozen_zdomain(alpha_min=0.02, alpha_max=0.30, num_alphas=7, fs=100.0):
    """
    Treats the load-adaptive filter as a quasi-static system.
    Computes Z-domain properties across a sweep of alpha values.
    
    Section 1.1 Derivation:
    The impulse response of a fixed EMA is h[n] = alpha * (1-alpha)^n.
    The DC group delay is derived from the mean of the impulse response:
    tau_g(0) = sum(n * h[n]) = sum(n * alpha * (1-alpha)^n).
    By properties of geometric series, this simplifies to (1-alpha) / alpha.
    """
    alphas = np.linspace(alpha_min, alpha_max, num_alphas)
    
    results = []
    for a in alphas:
        b = [a]
        a_poly = [1, -(1 - a)]
        
        z, p, k = scipy.signal.tf2zpk(b, a_poly)
        w, h = scipy.signal.freqz(b, a_poly, worN=2048, fs=fs)
        w_gd, gd = scipy.signal.group_delay((b, a_poly), w=2048, fs=fs)
        
        # DC group delay
        dc_gd = gd[0]
        expected_dc_gd = (1 - a) / a
        
        results.append({
            'alpha': a,
            'zeros': z,
            'poles': p,
            'freqs': w,
            'mag': 20 * np.log10(np.abs(h) + 1e-12),
            'phase': np.unwrap(np.angle(h)) * 180 / np.pi,
            'gd': gd,
            'w_gd': w_gd,
            'dc_gd': dc_gd,
            'expected_dc_gd': expected_dc_gd
        })
    return results

def plot_pole_zero_sweep(results, out_path="results/figures/pole_zero_sweep.png"):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Unit circle
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.5)
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(results)))
    
    for res, color in zip(results, colors):
        p = res['poles']
        ax.plot(np.real(p), np.imag(p), 'x', color=color, markersize=10, 
                label=rf"$\alpha$={res['alpha']:.3f}")
                
    ax.set_aspect('equal')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_title("Pole Locations vs Alpha")
    ax.set_xlabel("Real")
    ax.set_ylabel("Imaginary")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def plot_frequency_response_sweep(results, out_path="results/figures/frequency_response_sweep.png"):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
    colors = plt.cm.viridis(np.linspace(0, 1, len(results)))
    
    for res, color in zip(results, colors):
        label = rf"$\alpha$={res['alpha']:.3f}"
        ax1.plot(res['freqs'], res['mag'], color=color, label=label)
        ax2.plot(res['freqs'], res['phase'], color=color, label=label)
        
    ax1.set_ylabel("Magnitude (dB)")
    ax1.set_title("Frequency Response Sweep")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    ax2.set_ylabel("Phase (degrees)")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def plot_pole_trajectory_vs_load(L, pole_trajectory, time_axis, out_path="results/figures/pole_trajectory_vs_load.png"):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    ax1.plot(time_axis, pole_trajectory, 'b-', label="Pole Location (1 - α)", linewidth=1.5)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Pole Location (Z-domain real axis)", color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_ylim(0, 1.0)
    
    ax2 = ax1.twinx()
    ax2.plot(time_axis, L, 'r-', alpha=0.5, label="Normalized Backpressure (L)", linewidth=1.0)
    ax2.set_ylabel("Backpressure L[n]", color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.set_ylim(-0.05, 1.05)
    
    fig.suptitle("Pole Trajectory vs Load")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

"""
Derivation of slew-rate bound necessity:
For the frozen-time frequency response to be a valid approximation of the
filter's instantaneous behavior, the pole must move slowly relative to the 
filter's own time constant τ. If alpha changes too rapidly, the filter's output
will be dominated by transient ringing from the parameter change rather than
its steady-state response to the input signal. Bounding |alpha[n] - alpha[n-1]|
ensures the system remains quasi-static, allowing us to meaningfully interpret
its behavior using Z-domain analysis at any given instant.
"""
