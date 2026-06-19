import numpy as np
from src.queue_simulator import simulate_backpressure
from src.evaluate import compute_auc
from src.detection import detect_anomalies

def test_queue_simulator_synthetic_rate(capsys):
    """Regression test: 10 Hz evenly-spaced arrival stream must yield λ ≈ 10.0 ± 5%."""
    import re
    t = np.arange(100) * 0.1  # 10 Hz stream → λ = 10 events/s

    L = simulate_backpressure(t, burst_multiplier=2.0)

    captured = capsys.readouterr()
    # Parse the printed λ value numerically so the test isn't brittle to formatting
    match = re.search(r"λ\s*=\s*([\d.]+)", captured.out)
    assert match, f"Could not find λ in output: {captured.out}"
    computed_lambda = float(match.group(1))
    assert abs(computed_lambda - 10.0) / 10.0 < 0.05, (
        f"λ = {computed_lambda:.4f}, expected 10.0 ± 5%"
    )

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
