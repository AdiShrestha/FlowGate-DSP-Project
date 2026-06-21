import time
import numpy as np
import warnings
from numba.core.errors import NumbaWarning
from src.numba_filters import compute_processing_mask_kernel

warnings.simplefilter("error", category=NumbaWarning)

L = np.random.rand(200000)
# Warmup
compute_processing_mask_kernel(L[:10], 4)

t0 = time.time()
for _ in range(10):
    compute_processing_mask_kernel(L, 4)
t1 = time.time()

print(f"Mask kernel alone: {(t1-t0)/10 / 200000 * 1e6:.4f} ms/1k")
