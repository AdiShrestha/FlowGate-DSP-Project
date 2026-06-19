import numpy as np
import pandas as pd

def detect_anomalies(
    x: np.ndarray, 
    y: np.ndarray, 
    window: int = 100, 
    threshold: float = 3.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes residuals, normalized Z-scores, and binary detection flags.
    
    Parameters:
    - x: Raw (or anomaly-injected) input signal
    - y: Filtered signal
    - window: Rolling window size for residual standard deviation
    - threshold: Z-score threshold for flagging an anomaly
    
    Returns:
    - residual: x - y
    - z: Normalized residual
    - detected: Boolean array of flags
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    residual = x - y
    
    # Causal rolling std (trailing window only, no lookahead)
    r_series = pd.Series(residual)
    sigma_r = r_series.rolling(window=window, min_periods=1).std().bfill().values
    
    # Avoid division by zero
    sigma_r = np.where(sigma_r == 0, 1e-9, sigma_r)
    
    z = residual / sigma_r
    detected = np.abs(z) > threshold
    
    return residual, z, detected
