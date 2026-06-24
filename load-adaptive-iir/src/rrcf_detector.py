import rrcf
import numpy as np

def run_rrcf_streaming(x: np.ndarray,
                       num_trees: int = 40,
                       tree_size: int = 256,
                       shingle_size: int = 4) -> np.ndarray:
    """
    Run RRCF in pure streaming mode (FIFO tree, one point at a time).
    Returns: avg_codisp score array (higher = more anomalous), same length as x.
    """
    forest = [rrcf.RCTree() for _ in range(num_trees)]
    
    # We must handle shingling. `rrcf.shingle` returns a generator of points.
    # But since it's a generator, the first (shingle_size - 1) points might need padding 
    # or the output will be shorter. 
    # Actually `rrcf.shingle` pads with previous elements or requires a 1D array and returns
    # len(x) - size + 1 points.
    # For a fair streaming comparison, we want the output array to have the same length as `x`.
    # We will pad `x` at the beginning with the first element.
    padded_x = np.concatenate([np.full(shingle_size - 1, x[0]), x])
    points = rrcf.shingle(padded_x, size=shingle_size)
    
    avg_codisp = np.zeros(len(x))

    for idx, point in enumerate(points):
        # We use idx which ranges from 0 to len(x)-1
        for tree in forest:
            if len(tree.leaves) > tree_size:
                tree.forget_point(idx - tree_size)
            tree.insert_point(point, index=idx)
            
        codisp_vals = [tree.codisp(idx) for tree in forest if idx in tree.leaves]
        if codisp_vals:
            avg_codisp[idx] = np.mean(codisp_vals)

    return avg_codisp
