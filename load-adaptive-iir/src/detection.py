import numpy as np
import pandas as pd

def detect_anomalies(
    x: np.ndarray, 
    y: np.ndarray, 
    window: int = 100, 
    threshold: float = 3.0,
    estimator: str = 'std'
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes residuals, normalized Z-scores, and binary detection flags.
    
    Parameters:
    - x: Raw (or anomaly-injected) input signal
    - y: Filtered signal
    - window: Rolling window size for residual standard deviation
    - threshold: Z-score threshold for flagging an anomaly
    - estimator: 'std' or 'mad' for robust scale estimation
    
    Returns:
    - residual: x - y
    - z: Normalized residual
    - detected: Boolean array of flags
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    residual = x - y
    
    r_series = pd.Series(residual)
    if estimator == 'std':
        sigma_r = r_series.rolling(window=window, min_periods=1).std().bfill().values
    elif estimator == 'mad':
        def mad_calc(s):
            return np.median(np.abs(s - np.median(s)))
        sigma_r = r_series.rolling(window=window, min_periods=1).apply(mad_calc, raw=True).bfill().values * 1.4826
    
    # Avoid division by zero
    sigma_r = np.where(sigma_r == 0, 1e-9, sigma_r)
    
    z = residual / sigma_r
    detected = np.abs(z) > threshold
    
    return residual, z, detected
