import numpy as np
from src.queue_simulator import simulate_backpressure
from src.evaluate import compute_auc
from src.detection import detect_anomalies

def test_queue_simulator_synthetic_rate(capsys):
    t = np.arange(100) * 0.1 # 10 Hz stream
    
    # simulate_backpressure prints the lambda it calculated
    L = simulate_backpressure(t, burst_multiplier=2.0)
    
    captured = capsys.readouterr()
    # We want to assert that the computed lambda is approx 10.0
    # Let's see if "10.0" is in the output or we just print it to see what fails
    print("Simulate backpressure output:", captured.out)
    
    # This might fail with the current code, which is the point
    assert "λ = 10.00" in captured.out or "10.0" in captured.out, f"Expected lambda around 10, got {captured.out}"

def test_evaluate_trivial_case():
    n_samples = 1000
    x = np.random.normal(0, 1, n_samples)
    y = x.copy()
    
    # Inject 20 sigma spike
    spike_idx = 500
    x[spike_idx] += 20.0
    
    anomaly_info = [{'type': 'point', 'start': spike_idx, 'end': spike_idx}]
    
    _, z, _ = detect_anomalies(x, y)
    mask = np.zeros(n_samples, dtype=bool)
    mask[spike_idx] = True
    roc_auc, _, _, _, _, _ = compute_auc(z, anomaly_info, mask)
    
    assert roc_auc > 0.95, f"ROC AUC was {roc_auc}, expected > 0.95"
