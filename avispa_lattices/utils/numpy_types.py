import re
import numpy as np

npBoolMatrix = np.ndarray
npUInt64Matrix = np.ndarray
npInt64Array = np.ndarray

_get_dtype_string = re.compile(
    r'(<class \'numpy\.(.*)\'>)|(<class \'(.*?)\'>)|(.*)')


def get_dtype_string(dtype):
    'return the dtype string of a numpy dtype'
    m = _get_dtype_string.match(str(dtype))
    assert m
    g = m.groups()
    dtype_str: str = g[1] or g[3] or g[4]
    np_dtype = np.dtype(dtype_str)  # type:ignore
    assert dtype == np_dtype, (
        f'Non invertible dtype: {dtype} != np.dtype(\'{dtype_str}\')')
    return dtype_str
