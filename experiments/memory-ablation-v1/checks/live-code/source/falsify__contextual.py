"""Online past-item feature language; keeps the original evaluator untouched."""
import ctypes
import math
import random
import subprocess
import sys
from pathlib import Path
from .core import BEST_FIT, FEATURES

CONTEXT_FEATURES=FEATURES+['gap/100*(1-p_fit_gap)','nonzero_gap*(1-p_fit_gap)',
    'p_item_near_gap','nearest_past_item_distance/100','p_fit_gap',
    'gap/100*p_fit_gap','p_fit_remaining-p_fit_gap','gap/100*mean_past_item/100']
CONTEXT_BEST_FIT=BEST_FIT+[0.]*8
LIB=None

def pack_contextual(items,weights=CONTEXT_BEST_FIT,trace=False):
    global LIB
    if len(weights)!=20 or not all(isinstance(w,(int,float)) and math.isfinite(w) for w in weights):
        raise ValueError('Twenty finite feature weights required')
    if not all(isinstance(x,int) and not isinstance(x,bool) and 1<=x<=100 for x in items):
        raise ValueError('Items must be integers from 1 through 100')
    if LIB is None:
        source=Path(__file__).with_suffix('.cpp')
        binary=source.with_name('_contextual.dylib' if sys.platform=='darwin' else '_contextual.so')
        if not binary.exists() or binary.stat().st_mtime<source.stat().st_mtime:
            subprocess.run(['c++','-O3','-std=c++17','-shared','-fPIC',str(source),'-o',str(binary)],check=True)
        LIB=ctypes.CDLL(str(binary))
        LIB.pack_contextual.argtypes=[ctypes.POINTER(ctypes.c_int),ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int)]
        LIB.pack_contextual.restype=ctypes.c_int
    xs=(ctypes.c_int*len(items))(*items)
    ws=(ctypes.c_double*20)(*weights)
    assignments=(ctypes.c_int*len(items))() if trace else None
    bins=LIB.pack_contextual(xs,len(items),ws,assignments)
    if bins<0:raise ValueError('Invalid packing input or scores')
    return (bins,list(assignments)) if trace else bins

def mutate_contextual(weights,rng):
    child=list(weights)
    for _ in range(rng.choice([1,1,2,3,5])):
        j=rng.randrange(20)
        child[j]=max(-12.,min(12.,child[j]+rng.gauss(0,rng.choice([.1,.3,1.,3.]))))
    return child

class PreparedCase:
    """Validated immutable input buffer for repeated native evaluations."""
    def __init__(self,case):
        self.family=case['family']
        self.items=tuple(case['items'])
        if len(self.items)>4096 or not all(isinstance(x,int) and not isinstance(x,bool) and 1<=x<=100 for x in self.items):
            raise ValueError('Invalid prepared instance')
        self.buffer=(ctypes.c_int*len(self.items))(*self.items)

    def to_json(self):return {'family':self.family,'items':list(self.items)}

def evaluate_cases(cases,weights):
    if len(weights)!=20 or not all(isinstance(w,(int,float)) and math.isfinite(w) for w in weights):
        raise ValueError('Twenty finite feature weights required')
    if LIB is None:pack_contextual([],weights)
    ws=(ctypes.c_double*20)(*weights)
    results=[]
    for case in cases:
        score=LIB.pack_contextual(case.buffer,len(case.items),ws,None)
        if score<0:raise ValueError('Invalid native evaluation')
        results.append(score)
    return results

def anchors():
    definitions=[('best_fit',{}),
        ('avoid_unfillable_residual',{12:-.8,13:-.1}),
        ('match_future_mass',{14:.8}),
        ('nearest_observed_size',{0:-.2,3:1.,15:-.8}),
        ('tight_or_roomy_with_fit',{0:.25,2:3.,3:1.,4:-.02,12:-.15}),
        ('preserve_fit_opportunities',{18:-.4,14:.2})]
    out=[]
    for name,changes in definitions:
        w=list(CONTEXT_BEST_FIT)
        for j,v in changes.items():w[j]=v
        out.append({'name':name,'weights':w})
    return out
