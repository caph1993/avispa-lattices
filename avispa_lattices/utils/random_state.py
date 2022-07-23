from typing import Optional, Tuple, Union
import numpy as np

Shape = Union[int, Tuple[int, ...]]


class AL_RandomState(np.random.RandomState):

    def randint32(self, size: Optional[Shape] = None):
        low = np.iinfo(np.int32).min
        high = np.iinfo(np.int32).max
        return super().randint(low, high, size=size)

    def set_seed(self, seed: Optional[int] = None):
        super().seed(seed)


AL_random = AL_RandomState()