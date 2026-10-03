"""Standard-library harness with a tiny compiled evaluator for repeated trials."""
import ctypes
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FEATURES = ['gap/100', '(gap/100)^2', '1/(gap+1)', 'gap==0',
            '0<gap<10', '0<gap<item', 'gap>=item', 'abs(gap/100-.25)',
            'abs(gap/100-.5)', 'abs(gap/100-.75)', '0<gap<33', '0<gap<50']
BEST_FIT = [-1.] + [0.]*11
WORST_FIT = [1.] + [0.]*11

def load_library():
    source = ROOT/'packing.cpp'
    lib = ROOT/('_packing.dylib' if sys.platform == 'darwin' else '_packing.so')
    if not lib.exists() or lib.stat().st_mtime < source.stat().st_mtime:
        subprocess.run(['c++', '-O3', '-std=c++17', '-shared', '-fPIC', str(source), '-o', str(lib)], check=True)
    api = ctypes.CDLL(str(lib))
    api.pack.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int,
                         ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int)]
    api.pack.restype = ctypes.c_int
    return api

LIB = None

def pack(items, weights=BEST_FIT, trace=False):
    global LIB
    if LIB is None:
        LIB = load_library()
    if len(weights) != 12:
        raise ValueError('Exactly 12 finite feature weights required')
    xs = (ctypes.c_int*len(items))(*items)
    ws = (ctypes.c_double*12)(*weights)
    assignments = (ctypes.c_int*len(items))() if trace else None
    result = LIB.pack(xs, len(items), ws, assignments)
    if result < 0:
        raise ValueError('Invalid items, weights, or instance length')
    return (result, list(assignments)) if trace else result

TRAIN_FAMILIES = ['uniform', 'small', 'large', 'bimodal', 'complementary']
SHIFT_FAMILIES = ['near_thirds', 'near_halves', 'bands']

def instance(rng, family, n=80):
    if family == 'uniform': return [rng.randint(1,99) for _ in range(n)]
    if family == 'small': return [rng.randint(1,35) for _ in range(n)]
    if family == 'large': return [rng.randint(35,95) for _ in range(n)]
    if family == 'bimodal': return [rng.randint(5,20) if rng.random()<.5 else rng.randint(65,85) for _ in range(n)]
    if family == 'complementary':
        a = rng.randint(15,45)
        xs = [max(1,min(99,(a if rng.random()<.5 else 100-a)+rng.randint(-3,3))) for _ in range(n)]
        return xs
    if family == 'near_thirds': return [rng.randint(30,36) for _ in range(n)]
    if family == 'near_halves': return [rng.randint(47,53) for _ in range(n)]
    if family == 'bands': return [rng.choice([19,20,21,39,40,41,59,60,61,79,80,81]) for _ in range(n)]
    raise ValueError(family)

def suite(seed, count, families=TRAIN_FAMILIES):
    rng = random.Random(seed)
    return [{'family':families[i%len(families)], 'items':instance(rng,families[i%len(families)])} for i in range(count)]

def identity(items):
    return hashlib.sha256(bytes(items)).hexdigest()[:16]

def mutate(weights, rng):
    child = list(weights)
    for _ in range(rng.choice([1,1,2,3,5])):
        j = rng.randrange(12)
        child[j] += rng.gauss(0,rng.choice([.1,.3,1.,3.]))
        child[j] = max(-12.,min(12.,child[j]))
    return child

def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')
