import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from pathlib import Path
from src.filters import fixed_ema

def generate_synthetic_signal(fs=100.0, duration=10.0, seed=42):
    """
    Generates a canonical demo signal for DSP analysis.
    Contains a slow trend, fast oscillations, high frequency jitter, noise, and spikes.
    """
    np.random.seed(seed)
    n_samples = int(fs * duration)
    t = np.arange(n_samples) / fs
    
    # Components
    A1, f1 = 1.0, 0.2
    A2, f2 = 0.3, 5.0
    A3, f3 = 0.1, 20.0
    
    x = (A1 * np.sin(2 * np.pi * f1 * t) + 
         A2 * np.sin(2 * np.pi * f2 * t) + 
         A3 * np.sin(2 * np.pi * f3 * t))
         
    # Noise
    w = np.random.normal(0, 0.05, n_samples)
    x += w
    
    # Spikes
    spike_idx = np.random.choice(n_samples, size=5, replace=False)
    spikes = np.zeros(n_samples)
    spikes[spike_idx] = np.random.choice([-1, 1], size=5) * 2.0
    x += spikes
    
    return t, x

def plot_impulse_and_step_responses(alphas=[0.3, 0.1, 0.03], n_samples=50):
    """
    Plots the impulse and step responses for fixed/frozen EMA.
    """
    Path("results/figures").mkdir(parents=True, exist_ok=True)
    
    # Impulse
    delta = np.zeros(n_samples)
    delta[0] = 1.0
    
    fig_imp, ax_imp = plt.subplots(figsize=(8, 5))
    for a in alphas:
        y, _ = fixed_ema(delta, a)
        tau = -1 / np.log(1 - a)
        ax_imp.plot(y, marker='o', markersize=3, label=rf"$\alpha$={a} ($\tau$={tau:.1f})")
        
    ax_imp.set_title("Impulse Response")
    ax_imp.set_xlabel("Samples [n]")
    ax_imp.set_ylabel("Amplitude")
    ax_imp.legend()
    ax_imp.grid(True, alpha=0.3)
    fig_imp.tight_layout()
    fig_imp.savefig("results/figures/impulse_response.png", dpi=150)
    plt.close(fig_imp)
    
    # Step
    u = np.ones(n_samples)
    
    fig_step, ax_step = plt.subplots(figsize=(8, 5))
    for a in alphas:
        y, _ = fixed_ema(u, a)
        ax_step.plot(y, marker='o', markersize=3, label=rf"$\alpha$={a}")
        
    ax_step.axhline(1.0, color='k', linestyle='--', alpha=0.5, label="Steady State (1.0)")
    ax_step.set_title("Step Response")
    ax_step.set_xlabel("Samples [n]")
    ax_step.set_ylabel("Amplitude")
    ax_step.legend()
    ax_step.grid(True, alpha=0.3)
    fig_step.tight_layout()
    fig_step.savefig("results/figures/step_response.png", dpi=150)
    plt.close(fig_step)

def plot_synthetic_filtering(t, x, filter_func, filter_name, fs=100.0, **kwargs):
    """
    Plots time-domain and frequency-domain effects of a filter on synthetic data.
    """
    Path("results/figures").mkdir(parents=True, exist_ok=True)
    
    y, _ = filter_func(x, **kwargs)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Time domain
    zoom_idx = min(len(t), int(2.0 * fs))
    ax1.plot(t[:zoom_idx], x[:zoom_idx], color='lightgray', label='Raw Signal')
    ax1.plot(t[:zoom_idx], y[:zoom_idx], color='blue', linewidth=2, label=f'Filtered ({filter_name})')
    ax1.set_title(f"Time Domain: {filter_name}")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Frequency domain
    f_x, Pxx_x = scipy.signal.welch(x, fs, nperseg=1024)
    f_y, Pxx_y = scipy.signal.welch(y, fs, nperseg=1024)
    
    ax2.plot(f_x, 10 * np.log10(Pxx_x), color='lightgray', label='Raw Signal')
    ax2.plot(f_y, 10 * np.log10(Pxx_y), color='blue', label=f'Filtered ({filter_name})')
    
    for f_target in [0.2, 5.0, 20.0]:
        ax2.axvline(f_target, color='r', linestyle='--', alpha=0.5)
        
    ax2.set_title("Power Spectral Density (Welch)")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Power/Frequency (dB/Hz)")
    ax2.set_xlim(0, fs/2)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    # Normalize filename
    safe_name = filter_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
    if safe_name == "load_adaptive_ema":
        safe_name = "load_adaptive"
    fig.savefig(f"results/figures/spectrum_demo_{safe_name}.png", dpi=150)
    plt.close(fig)

def plot_real_data_psd(price_series, fs, y_dict):
    """
    Plots the PSD comparison on real tick data across multiple filters.
    """
    Path("results/figures").mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    f_x, Pxx_x = scipy.signal.welch(price_series, fs, nperseg=min(1024, len(price_series)))
    ax.plot(f_x, 10 * np.log10(Pxx_x), color='lightgray', linewidth=2, label='Raw Price')
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    for (name, y), color in zip(y_dict.items(), colors):
        f_y, Pxx_y = scipy.signal.welch(y, fs, nperseg=min(1024, len(y)))
        ax.plot(f_y, 10 * np.log10(Pxx_y), color=color, alpha=0.8, label=name)
        
    ax.set_title("PSD Comparison on Real Tick Data")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power/Frequency (dB/Hz)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig("results/figures/psd_comparison_real_data.png", dpi=150)
    plt.close(fig)

def plot_time_varying_frequency_response(alpha_trace, L_trace, fs=100.0, num_blocks=100):
    """
    Flagship visualization: A spectrogram-like heatmap of the filter's own frequency response
    over time, overlaid with the backpressure signal.
    """
    Path("results/figures").mkdir(parents=True, exist_ok=True)
    
    n_samples = len(alpha_trace)
    block_size = max(1, n_samples // num_blocks)
    
    alphas_downsampled = alpha_trace[::block_size][:num_blocks]
    L_downsampled = L_trace[::block_size][:num_blocks]
    time_blocks = np.arange(len(alphas_downsampled)) * block_size / fs
    
    # Compute freqz for each block
    w_grid = np.linspace(0, np.pi, 200) # normalized freq
    f_grid = w_grid * fs / (2 * np.pi)
    
    mag_db_matrix = np.zeros((len(f_grid), len(alphas_downsampled)))
    
    for i, a in enumerate(alphas_downsampled):
        b = [a]
        a_poly = [1, -(1 - a)]
        _, h = scipy.signal.freqz(b, a_poly, worN=w_grid)
        mag_db_matrix[:, i] = 20 * np.log10(np.abs(h) + 1e-12)
        
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [1, 3]}, sharex=True)
    
    # Top plot: L[n]
    ax1.plot(time_blocks, L_downsampled, 'r-', label='Backpressure L[n]', linewidth=2)
    ax1.set_ylabel("Load L[n]")
    ax1.set_title("Time-Varying Filter Characteristics Driven by Load")
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Bottom plot: Heatmap
    X, Y = np.meshgrid(time_blocks, f_grid)
    pcm = ax2.pcolormesh(X, Y, mag_db_matrix, shading='auto', cmap='viridis', vmin=-40, vmax=0)
    ax2.set_ylabel("Frequency (Hz)")
    ax2.set_xlabel("Time (s)")
    
    cbar = fig.colorbar(pcm, ax=ax2, orientation='vertical')
    cbar.set_label('Magnitude (dB)')
    
    fig.tight_layout()
    fig.savefig("results/figures/time_varying_frequency_response.png", dpi=150)
    plt.close(fig)
