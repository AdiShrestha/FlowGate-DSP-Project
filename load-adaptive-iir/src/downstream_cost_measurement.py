import socket
import time
import numpy as np
import json
from pathlib import Path

def measure_udp_localhost_latency(n_trials: int = 10000) -> dict:
    """
    Measure per-send latency of UDP to localhost as a downstream I/O surrogate.
    This represents a minimal 'send an alert/event' cost downstream of the filter.
    Returns p50, p95, p99, mean, std in microseconds.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = b'{"price": 42300.5, "alert": true}'   # realistic-size alert payload
    addr = ('127.0.0.1', 9999)

    # Warm up
    for _ in range(100):
        sock.sendto(payload, addr)

    # Measure
    times = []
    for _ in range(n_trials):
        t0 = time.perf_counter()
        sock.sendto(payload, addr)
        times.append((time.perf_counter() - t0) * 1e6)   # microseconds
    sock.close()

    times = np.array(times)
    result = {
        'p50_us': float(np.percentile(times, 50)),
        'p95_us': float(np.percentile(times, 95)),
        'p99_us': float(np.percentile(times, 99)),
        'mean_us': float(np.mean(times)),
        'std_us': float(np.std(times)),
        'n_trials': n_trials
    }
    return result

if __name__ == "__main__":
    print("Measuring UDP localhost latency...")
    result = measure_udp_localhost_latency()
    
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    out_path = Path("results/tables/downstream_cost_measurement.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=4)
        
    print(json.dumps(result, indent=4))
    print(f"Replacing modeled 5µs with measured p50={result['p50_us']:.2f}µs")
