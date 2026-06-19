import numpy as np
import pandas as pd

def inject_anomalies(
    x: pd.Series, 
    n_each: int = 5, 
    window_std: int = 100, 
    seed: int = 42
) -> tuple[np.ndarray, np.ndarray, list]:
    """
    Injects synthetic anomalies into a clean time series.
    Returns:
        x_injected (np.ndarray): The series with injected anomalies.
        mask (np.ndarray): Boolean mask indicating anomaly locations.
        anomaly_info (list): List of dicts with details of each injected anomaly.
    """
    np.random.seed(seed)
    
    x_injected = x.values.copy()
    n_samples = len(x_injected)
    mask = np.zeros(n_samples, dtype=bool)
    
    # Pre-calculate rolling std
    rolling_std = x.rolling(window=window_std, min_periods=1).std().bfill().values
    
    # Avoid first 500 samples (let filters settle) and last 500
    buffer = 500
    if n_samples <= 2 * buffer:
        raise ValueError("Series too short for anomaly injection")
        
    available_indices = np.arange(buffer, n_samples - buffer)
    
    anomaly_info = []
    
    # Helper to remove used indices
    def remove_used(idx, span):
        nonlocal available_indices
        used_mask = (available_indices >= idx - span) & (available_indices <= idx + span)
        available_indices = available_indices[~used_mask]

    # 1. Point anomalies (single sample, magnitude = k * rolling_std, k=8)
    for _ in range(n_each):
        if len(available_indices) == 0: break
        idx = np.random.choice(available_indices)
        k = 8.0 * np.random.choice([-1, 1])
        x_injected[idx] += k * rolling_std[idx]
        mask[idx] = True
        anomaly_info.append({'type': 'point', 'start': idx, 'end': idx})
        remove_used(idx, 300)

    # 2. Level shift (w=50-200, magnitude = k * rolling_std, k=8)
    for _ in range(n_each):
        if len(available_indices) == 0: break
        idx = np.random.choice(available_indices)
        w = np.random.randint(50, 200)
        k = 8.0 * np.random.choice([-1, 1])
        x_injected[idx:idx+w] += k * rolling_std[idx]
        mask[idx:idx+w] = True
        anomaly_info.append({'type': 'level_shift', 'start': idx, 'end': idx+w-1})
        remove_used(idx, w + 300)
        
    # 3. Volatility burst (multiply local returns by 5x, window=50-200)
    for _ in range(n_each):
        if len(available_indices) == 0: break
        idx = np.random.choice(available_indices)
        w = np.random.randint(50, 200)
        
        segment = x_injected[idx:idx+w]
        if len(segment) > 1:
            ret = np.diff(segment, prepend=segment[0])
            ret[1:] *= 5.0 # Inflate variance
            
            new_segment = np.cumsum(ret)
            new_segment += (segment[0] - new_segment[0])
            
            x_injected[idx:idx+w] = new_segment
            
        mask[idx:idx+w] = True
        anomaly_info.append({'type': 'volatility_burst', 'start': idx, 'end': idx+w-1})
        remove_used(idx, w + 300)
        
    return x_injected, mask, anomaly_info
