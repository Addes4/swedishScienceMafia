"""Tuning grid (training-style data only): CDF-weighted SS with the volume switch, over beta, alpha and c.

Usage: python experiments/online-beyond-ss-v1/tuning_grid.py   (writes tuning_grid.json; a few minutes)
Sets: verify.items_for seeds 90000-90099; EoH generator seeds 777000+; uniform 20-100 sizes seeds 888000+.
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
from sim import l1, weibull_items
from fast import pack_wss, pack_wss_vol, pack_fss, wpow
from frontier_snapshot import pack_funsearch, FS_W, FS_OR
def eoh_like(seed, n):
    rng = np.random.default_rng(seed); return np.round(np.clip(rng.weibull(3, n)*45, 1, 100)).astype(int).tolist()
def unif(seed, n):
    rng = np.random.default_rng(seed); return rng.integers(20, 101, n).tolist()
sets = []
sets.append(('FS-trunc 5k C100', [weibull_items(sd, 5000) for sd in range(90000, 90100)], 100))
for n in [1000, 5000]:
    for C in [100, 500]:
        sets.append((f'EoH {n//1000}k C{C}', [eoh_like(777000 + 10*n + C + k, n) for k in range(20)], C))
for n in [120, 250, 500, 1000]:
    sets.append((f'Unif {n} C150', [unif(888000 + n + k, n) for k in range(60)], 150))
configs = [('SS', None)] + [((b, a, c), None) for b in [1, 1.5, 2, 2.5, 3] for a in [0, 0.5, 1] for c in [1.1, 1.3, 1.5, 2.0]]
table = {}
for label, insts, C in sets:
    L = np.array([l1(x, C) for x in insts])
    ex = lambda v: 100*(sum(v)-L.sum())/L.sum()
    ref = min(ex([pack_funsearch(x, C, FS_W) for x in insts]), ex([pack_funsearch(x, C, FS_OR) for x in insts]))
    table[label] = {'FSbest': ref, 'SS': ex([pack_wss(x, C, [1.0]*(C+1), 0) for x in insts]), 'BF': ex([pack_wss(x, C, [1.0]*(C+1), len(x)) for x in insts])}
    for (cfg, _) in configs[1:]:
        b, a, c = cfg
        table[label][str(cfg)] = ex([pack_fss(x, C, b, c, a) for x in insts])
    print(label, 'FSbest %.3f SS %.3f BF %.3f' % (ref, table[label]['SS'], table[label]['BF']), flush=True)
json.dump(table, open(str(HERE / 'tuning_grid.json'), 'w'))
# rank configs: geometric mean of excess / min(SS, FSbest, BF) across sets, and count of sets where it beats min(SS,FSbest,BF)
rows=[]
for (cfg, _) in configs[1:]:
    k=str(cfg); r=[]; wins=0
    for lab in table:
        base=min(table[lab]['SS'], table[lab]['FSbest'], table[lab]['BF']); r.append(table[lab][k]/base); wins += table[lab][k] < base
    rows.append((float(np.exp(np.mean(np.log(r)))), wins, k))
rows.sort()
for gm, wins, k in rows[:15]: print(f'{k:20s} geo-mean ratio to best baseline {gm:.3f}  beats best baseline in {wins}/{len(table)}  ' + ' '.join(f'{table[l][k]:.3f}' for l in table))
