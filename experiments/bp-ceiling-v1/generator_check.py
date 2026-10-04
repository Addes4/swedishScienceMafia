"""Which rounding did FunSearch's Weibull generator use? Fits the released Weibull 5k test items.

The Supplementary Information (E.4) says Weibull(45, 3) samples were clipped at 100 and rounded
to the nearest integer. This compares the 25,000 released items with the exact probabilities
under rounding and under truncation (int()), and writes generator_check.json.

    python experiments/bp-ceiling-v1/generator_check.py
"""
import gzip
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent


def pmf(mode, scale=45.0, shape=3.0):
    sizes = np.arange(1, 101, dtype=float)
    cdf = lambda x: 1 - np.exp(-(np.clip(x, 0, None) / scale) ** shape)
    if mode == 'round':
        lo, hi = sizes - 0.5, sizes + 0.5
    else:
        lo, hi = sizes, sizes + 1
    lo[0] = 0.0                          # everything below the smallest size is clipped up to 1
    p = cdf(hi) - cdf(lo)
    p[-1] = 1 - cdf(lo[-1])              # everything above 100 is clipped down to 100
    return p / p.sum()


def main():
    with gzip.open(HERE / 'funsearch_weibull5k_test.json.gz', 'rt') as f:
        data = json.load(f)['instances']
    items = np.concatenate([np.array(v['items']) for v in data.values()])
    observed = np.bincount(items, minlength=101)[1:]
    out = {'items': int(len(items)), 'observed_mean': float(items.mean()), 'observed_sd': float(items.std(ddof=1))}
    for mode in ['round', 'truncate']:
        p = pmf(mode)
        expected = p * len(items)
        mean = float((np.arange(1, 101) * p).sum())
        keep = expected >= 5
        o = np.append(observed[keep], observed[~keep].sum())
        e = np.append(expected[keep], expected[~keep].sum())
        chi2 = float(((o - e) ** 2 / e).sum())
        out[mode] = {'expected_mean': mean,
                     'z_of_observed_mean': (out['observed_mean'] - mean) / (out['observed_sd'] / math.sqrt(len(items))),
                     'chi2': chi2, 'df': int(len(o) - 1), 'p_value': float(stats.chi2.sf(chi2, len(o) - 1))}
    (HERE / 'generator_check.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
