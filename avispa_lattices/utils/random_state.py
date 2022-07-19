from typing import Optional
import numpy as np


def random_state(seed: Optional[int] = None):
    if seed is None:
        seed = np.random.randint(0, np.iinfo(np.int32).min)
    return np.random.RandomState(seed=seed)
