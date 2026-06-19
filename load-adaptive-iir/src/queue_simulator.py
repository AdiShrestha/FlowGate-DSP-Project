import numpy as np
import pandas as pd

def simulate_backpressure(
    timestamps: pd.Series,
    mu: float = None,
    target_rho: float = 0.75,
    q_max_percentile: float = 99.0,
    burst_multiplier: float = 1.0,
    burst_intervals: list = None
) -> pd.Series:
    """
    Simulates a single-server queue to generate a backpressure/load signal L[n].
    
    Parameters:
    - timestamps: pd.Series of event timestamps (in seconds).
    - mu: Service rate (events/sec). If None, calculated from target_rho.
    - target_rho: Target average utilization (lambda / mu). Used if mu is None.
    - q_max_percentile: Percentile of queue depth to use for normalization to L=1.
    - burst_multiplier: Multiplier for arrivals during burst intervals.
    - burst_intervals: List of tuples (start_idx, end_idx) where bursts occur.
    
    Returns:
    - pd.Series: Normalized backpressure signal L[n] in [0, 1].
    """
    n_samples = len(timestamps)
    
    if n_samples < 2:
        return pd.Series(np.zeros(n_samples), index=timestamps.index, name='L')
        
    # Calculate time differences in seconds
    t = np.asarray(timestamps)
    dt = np.diff(t)
    dt = np.insert(dt, 0, np.mean(dt)) # Assume first step is avg
    
    # Prevent negative time steps if unsorted or identical timestamps exist
    dt = np.maximum(dt, 0)
    
    # Arrival rate lambda
    total_time = t[-1] - t[0]
    avg_lambda = n_samples / total_time if total_time > 0 else 1.0
    
    if mu is None:
        mu = avg_lambda / target_rho
        print(f"Queue Simulator: avg arrival rate λ = {avg_lambda:.2f} events/s")
        print(f"Queue Simulator: setting service rate μ = {mu:.2f} events/s (target ρ = {target_rho})")
        
    arrivals = np.ones(n_samples)
    
    if burst_intervals and burst_multiplier != 1.0:
        for (start_idx, end_idx) in burst_intervals:
            start_idx = max(0, start_idx)
            end_idx = min(n_samples, end_idx)
            arrivals[start_idx:end_idx] *= burst_multiplier
            
    q = np.zeros(n_samples)
    
    # Discrete-event state update
    for i in range(1, n_samples):
        service_capacity = mu * dt[i]
        q[i] = max(0, q[i-1] + arrivals[i] - service_capacity)
        
    # Normalize
    q_max = np.percentile(q, q_max_percentile)
    if q_max == 0:
        q_max = 1e-9 # Prevent division by zero
        
    L = np.clip(q / q_max, 0.0, 1.0)
    
    if hasattr(timestamps, 'index'):
        return pd.Series(L, index=timestamps.index, name='L')
    return pd.Series(L, name='L')
