"""ctypes wrapper for csrc/wss.c (build: cc -O3 -shared -fPIC -o csrc/libwss.so csrc/wss.c)."""
import ctypes
from pathlib import Path

import numpy as np

_lib = ctypes.CDLL(str(Path(__file__).resolve().parent / "csrc" / "libwss.so"))
_lib.pack_wss.restype = ctypes.c_int
_lib.pack_wss.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int,
                          ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.POINTER(ctypes.c_int)]


_lib.pack_wss_vol.restype = ctypes.c_int
_lib.pack_wss_vol.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_double), ctypes.c_double,
                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]


def pack_wss_vol(items, C, w, c, return_state=False):
    """Weighted SS, then best fit once (items left) x (mean size so far) <= c x (total open gap)."""
    a = np.ascontiguousarray(items, dtype=np.int32)
    wv = np.ascontiguousarray(w, dtype=np.float64)
    N = np.zeros(C + 1, dtype=np.int32)
    sw = ctypes.c_int(0)
    b = _lib.pack_wss_vol(a.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), len(a), C,
                          wv.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), float(c),
                          N.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), ctypes.byref(sw))
    return (b, N, sw.value) if return_state else b


def pack_wss(items, C, w, K=0, return_state=False):
    a = np.ascontiguousarray(items, dtype=np.int32)
    wv = np.ascontiguousarray(w, dtype=np.float64)
    assert len(wv) == C + 1
    N = np.zeros(C + 1, dtype=np.int32)
    b = _lib.pack_wss(a.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), len(a), C,
                      wv.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), K,
                      N.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
    return (b, N) if return_state else b


def wpow(alpha, C):
    return [0.0] + [g ** -float(alpha) for g in range(1, C + 1)]


_lib.pack_fss.restype = ctypes.c_int
_lib.pack_fss.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double,
                          ctypes.c_double, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]


def pack_fss(items, C, beta, c, alpha=0.0, return_state=False):
    """SS weighted by F(g)^-beta * g^-alpha (F = online empirical CDF), then best fit by the volume switch c."""
    a = np.ascontiguousarray(items, dtype=np.int32)
    N = np.zeros(C + 1, dtype=np.int32)
    sw = ctypes.c_int(0)
    b = _lib.pack_fss(a.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), len(a), C, float(beta), float(alpha), float(c),
                      N.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), ctypes.byref(sw))
    return (b, N, sw.value) if return_state else b
