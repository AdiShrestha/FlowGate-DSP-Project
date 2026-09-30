import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'load-adaptive-iir')))
from src.filters import fixed_ema, load_adaptive_ema
from src.queue_simulator import simulate_backpressure
from src.anomaly_injection import inject_anomalies

print("Imports successful")
try:
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'load-adaptive-iir', 'data', 'processed', 'binance_BTCUSDT_20240102_20240102.parquet'))
    df = pd.read_parquet(data_path)
    df = df.iloc[5000:7000].copy().reset_index(drop=True)
    
    x_injected, mask, anomaly_info = inject_anomalies(df['price'], n_each=2, window_std=50)
    df['price_injected'] = x_injected
    
    L_full = simulate_backpressure(
        df['timestamp'],
        target_rho=0.75, 
        burst_multiplier=5.0, 
        burst_intervals=[(300, 500), (1200, 1400)]
    ).values
    
    y_fixed, _ = fixed_ema(x_injected, alpha=0.30)
    y_adaptive, pole_adaptive = load_adaptive_ema(x_injected, L_full, alpha_min=0.02, alpha_max=0.30)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
