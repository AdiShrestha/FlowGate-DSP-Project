import numpy as np
import scipy.signal

def fixed_ema(x: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Fixed-pole Exponential Moving Average (first-order IIR low-pass filter).

    Spec §1.1:
        y[n] = alpha*x[n] + (1-alpha)*y[n-1]
        H(z)  = alpha / (1 - (1-alpha)*z⁻¹)
        Pole location: z_pole = 1 - alpha

    DC group delay derivation (§1.1):
        The impulse response is h[n] = alpha*(1-alpha)^n  for n >= 0.
        Group delay at DC is the mean of h[n]:
            tau_g(0) = sum_{n=0}^{inf} n * h[n]
                     = alpha * sum_{n=0}^{inf} n*(1-alpha)^n
                     = alpha * (1-alpha) / alpha^2          [geometric series identity]
                     = (1-alpha) / alpha
        Numerically verified against scipy.signal.group_delay at w→0 in tests/test_filters.py.

    Parameters:
    - x:     Input signal array.
    - alpha: Smoothing factor (0 < alpha < 1).

    Returns:
    - y:               Filtered signal array (same length as x).
    - pole_trajectory: Constant array of pole locations (1 - alpha) for every sample.
    """
    x = np.asarray(x)
    n_samples = len(x)
    y = np.zeros(n_samples)
    y[0] = x[0]

    for n in range(1, n_samples):
        y[n] = alpha * x[n] + (1 - alpha) * y[n-1]

    pole_trajectory = np.full(n_samples, 1 - alpha)
    return y, pole_trajectory

def load_adaptive_ema(
    x: np.ndarray, 
    L: np.ndarray, 
    alpha_min: float = 0.02, 
    alpha_max: float = 0.30, 
    d_alpha_max: float = 0.01
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load-adaptive EMA.
    Section 1.2: alpha[n] = alpha_max - (alpha_max - alpha_min) * L[n]
    Section 1.3: Slew-rate limit |alpha[n] - alpha[n-1]| <= d_alpha_max
    
    Contrast with volatility-driven filters:
    This filter widens its effective window under high backpressure (lower alpha)
    to conserve downstream processing capacity, rather than speeding up under
    high signal activity like KAMA.
    """
    x = np.asarray(x)
    L = np.asarray(L)
    n_samples = len(x)
    
    alpha = np.zeros(n_samples)
    
    # Initialize first alpha
    a_init = alpha_max - (alpha_max - alpha_min) * L[0]
    alpha[0] = np.clip(a_init, 1e-4, 1 - 1e-4)
    
    for n in range(1, n_samples):
        target_a = alpha_max - (alpha_max - alpha_min) * L[n]
        
        diff = target_a - alpha[n-1]
        diff = np.clip(diff, -d_alpha_max, d_alpha_max)
        
        alpha[n] = np.clip(alpha[n-1] + diff, 1e-4, 1 - 1e-4)
        
    y = np.zeros(n_samples)
    y[0] = x[0]
    for n in range(1, n_samples):
        y[n] = alpha[n] * x[n] + (1 - alpha[n]) * y[n-1]

    # Return pole trajectory directly from alpha to avoid floating-point
    # round-trip error (1 - (1 - alpha) ≠ alpha exactly in IEEE 754).
    pole_trajectory = 1.0 - alpha
    return y, pole_trajectory

def kama(
    x: np.ndarray, 
    er_period: int = 10, 
    fast_period: int = 2, 
    slow_period: int = 30
) -> tuple[np.ndarray, np.ndarray]:
    """
    Kaufman's Adaptive Moving Average (KAMA).
    This is a signal-driven adaptive baseline (volatility/efficiency-driven),
    the conceptual contrast to the load-driven filter.
    """
    x = np.asarray(x)
    n_samples = len(x)
    y = np.zeros(n_samples)
    sc_trajectory = np.zeros(n_samples)
    
    fastSC = 2 / (fast_period + 1)
    slowSC = 2 / (slow_period + 1)
    
    # Initialize
    y[:er_period] = x[:er_period]
    sc_trajectory[:er_period] = slowSC
    
    # Pre-calculate absolute price changes
    change = np.abs(np.diff(x, prepend=x[0]))
    
    for n in range(er_period, n_samples):
        dir_change = abs(x[n] - x[n - er_period])
        volatility = np.sum(change[n - er_period + 1 : n + 1])
        
        er = dir_change / volatility if volatility != 0 else 0
        
        sc = (er * (fastSC - slowSC) + slowSC) ** 2
        sc_trajectory[n] = sc
        
        y[n] = y[n-1] + sc * (x[n] - y[n-1])
        
    pole_trajectory = 1 - sc_trajectory
    return y, pole_trajectory

def butterworth_lowpass(
    x: np.ndarray, 
    order: int = 4, 
    cutoff_hz: float = 1.0, 
    fs: float = 100.0
) -> tuple[np.ndarray, np.ndarray]:
    """
    Butterworth low-pass filter via explicit bilinear transform.
    """
    x = np.asarray(x)
    
    # 1. Analog prototype design
    omega_c = 2 * np.pi * cutoff_hz
    z_a, p_a, k_a = scipy.signal.butter(order, omega_c, btype='low', analog=True, output='zpk')
    
    # 2. Bilinear transform: s -> z substitution
    # Maps the s-domain (analog) poles/zeros to z-domain (digital)
    z_d, p_d, k_d = scipy.signal.bilinear_zpk(z_a, p_a, k_a, fs)
    
    # 3. Convert ZPK to transfer function polynomials (b, a)
    b, a = scipy.signal.zpk2tf(z_d, p_d, k_d)
    
    # 4. Filter the signal
    y = scipy.signal.lfilter(b, a, x)
    
    # Trajectory of digital poles (constant for all n)
    n_samples = len(x)
    # Returning a 2D array of poles (n_samples x order)
    pole_trajectory = np.tile(p_d, (n_samples, 1))
    
    return y, pole_trajectory
