from typing import Optional
import numpy as np


def random_state(seed: Optional[int] = None):
    if seed is None:
        high = np.iinfo(np.int32).max
        seed = np.random.randint(0, high)
    return np.random.RandomState(seed=seed)
