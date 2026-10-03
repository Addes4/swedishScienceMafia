"""Paired statistics for seed-matched comparisons (standard library only)."""
import math
import random
import statistics


def bootstrap_interval(values, resamples=10000, seed=739):
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(values, k=len(values))) for _ in range(resamples))
    return [means[int(.025*resamples)], means[int(.975*resamples)-1]]


def sign_test(wins, losses):
    """Exact two-sided sign test; ties are dropped."""
    n = wins+losses
    if n == 0: return 1.
    tail = sum(math.comb(n, k) for k in range(min(wins, losses)+1))/2**n
    return min(1., 2*tail)


def holm(pvalues):
    """Holm-Bonferroni adjusted p-values, same order as the input."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [0.]*len(pvalues), 0.
    for rank, i in enumerate(order):
        running = max(running, min(1., (len(pvalues)-rank)*pvalues[i]))
        adjusted[i] = running
    return adjusted


def paired(differences, tolerance=1e-12):
    """Summary of per-seed differences oriented so that positive favours the first arm."""
    wins = sum(d > tolerance for d in differences)
    losses = sum(d < -tolerance for d in differences)
    sd = statistics.stdev(differences) if len(differences) > 1 else 0.
    return {'n': len(differences), 'mean': statistics.fmean(differences),
            'interval95': bootstrap_interval(differences), 'wins': wins, 'losses': losses,
            'ties': len(differences)-wins-losses, 'sign_p': sign_test(wins, losses),
            'effect_dz': statistics.fmean(differences)/sd if sd > 0 else 0.}


def cluster_interval(groups, statistic=None, resamples=10000, seed=739):
    """95% bootstrap interval that resamples whole clusters (e.g. all switch moments of one seed).

    `groups` is a list of per-cluster value lists; `statistic` maps the pooled values of a resample
    to a number (default: their mean). Empty clusters are allowed."""
    statistic = statistic or statistics.fmean
    rng, stats = random.Random(seed), []
    for _ in range(resamples):
        pooled = [v for g in rng.choices(groups, k=len(groups)) for v in g]
        if pooled: stats.append(statistic(pooled))
    stats.sort()
    return [stats[int(.025*len(stats))], stats[int(.975*len(stats))-1]]
