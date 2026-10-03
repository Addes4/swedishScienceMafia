"""Benchmarks. Each exposes the four research moves the controller chooses between.

Scores are minimised. Moves return new solutions and never mutate their inputs.
To add a benchmark, subclass Problem and implement random/score/edit/rewrite/crossover.
"""
import itertools
import math
import random


class Problem:
    name = 'problem'
    higher_is_better = False                  # orientation of display(), for reports only

    def random(self, rng): raise NotImplementedError             # restart: a fresh solution
    def score(self, x): raise NotImplementedError                # lower is better
    def edit(self, x, rng): raise NotImplementedError            # small local change
    def rewrite(self, x, rng): raise NotImplementedError         # large change that keeps part of x
    def crossover(self, x, y, rng): raise NotImplementedError    # combine two solutions
    def display(self, score): return score                       # natural units for reports
    def describe(self, x): return repr(x)
    def oriented(self, delta): return delta if self.higher_is_better else -delta   # positive = better


class BitString(Problem):
    """Shared moves for fixed-length bit strings stored as Python ints."""
    def __init__(self, n):
        self.n, self.mask = n, (1 << n)-1

    def random(self, rng): return rng.getrandbits(self.n)
    def edit(self, x, rng): return x ^ (1 << rng.randrange(self.n))

    def segment(self, rng, lo, hi):
        """Mask of a random cyclic segment whose length is in [lo, hi]."""
        length, start = rng.randint(lo, hi), rng.randrange(self.n)
        m = (1 << length)-1
        return ((m << start) | (m >> (self.n-start))) & self.mask

    def rewrite(self, x, rng):
        block = self.segment(rng, self.n//4, self.n//2)
        return (x & ~block | rng.getrandbits(self.n) & block) & self.mask

    def crossover(self, x, y, rng):
        block = self.segment(rng, 1, self.n-1)
        return (x & ~block | y & block) & self.mask

    def describe(self, x): return format(x, f'0{self.n}b')


class LABS(BitString):
    """Low-autocorrelation binary sequences: minimise E = sum_k C_k^2; reported as merit factor n^2/2E."""
    higher_is_better = True

    def __init__(self, n=40):
        super().__init__(n)
        self.name = f'labs{n}'
        self.windows = [(1 << (n-k))-1 for k in range(n)]

    def score(self, x):
        n, energy = self.n, 0
        for k in range(1, n):
            c = (n-k) - 2*((x ^ (x >> k)) & self.windows[k]).bit_count()
            energy += c*c
        return energy

    def display(self, energy): return self.n*self.n/(2*energy)


class NK(BitString):
    """Kauffman NK landscape with random neighbours; K controls ruggedness. Reported as fitness."""
    higher_is_better = True

    def __init__(self, n=48, k=6, seed=0):
        super().__init__(n)
        self.name = f'nk{n}k{k}'
        rng = random.Random(f'nk/{n}/{k}/{seed}')
        self.links = [[i]+rng.sample([j for j in range(n) if j != i], k) for i in range(n)]
        self.tables = [[rng.random() for _ in range(1 << (k+1))] for _ in range(n)]

    def score(self, x):
        total = 0.
        for links, table in zip(self.links, self.tables):
            index = 0
            for j in links: index = index << 1 | (x >> j & 1)
            total += table[index]
        return -total/self.n

    def display(self, score): return -score


class Heilbronn(Problem):
    """Place n points in the unit square to maximise the smallest triangle area."""
    higher_is_better = True

    def __init__(self, n=12):
        self.n, self.name = n, f'heilbronn{n}'
        self.triples = list(itertools.combinations(range(n), 3))

    def random(self, rng): return tuple((rng.random(), rng.random()) for _ in range(self.n))

    def score(self, pts):
        smallest = math.inf
        for i, j, k in self.triples:
            (ax, ay), (bx, by), (cx, cy) = pts[i], pts[j], pts[k]
            area = abs((bx-ax)*(cy-ay)-(cx-ax)*(by-ay))
            if area < smallest: smallest = area
        return -smallest/2

    def edit(self, pts, rng):
        i, sigma = rng.randrange(self.n), rng.choice([.003, .01, .03])
        x, y = pts[i]
        moved = (min(1., max(0., x+rng.gauss(0, sigma))), min(1., max(0., y+rng.gauss(0, sigma))))
        return pts[:i]+(moved,)+pts[i+1:]

    def rewrite(self, pts, rng):
        out = list(pts)
        for i in rng.sample(range(self.n), max(2, self.n//3)): out[i] = (rng.random(), rng.random())
        return tuple(out)

    def crossover(self, a, b, rng):
        # Geometric cut: keep a's points on one side of a random axis-aligned line, b's on the other.
        axis, cut = rng.randrange(2), rng.random()
        side_a = [p for p in a if p[axis] < cut]
        side_b = [p for p in b if p[axis] >= cut]
        out = side_a+side_b
        rng.shuffle(out)
        spare = [p for p in a+b if p not in out]
        while len(out) < self.n:
            out.append(spare.pop(rng.randrange(len(spare))) if spare else (rng.random(), rng.random()))
        return tuple(out[:self.n])

    def display(self, score): return -score


class BinPacking(Problem):
    """The team's online bin-packing heuristic space (falsify/): 12 bin-scoring weights.

    Scored as mean bins over a fixed suite; reported as mean excess bins over best-fit.
    """
    def __init__(self, seed=0, cases=24):
        from falsify.core import BEST_FIT, mutate, pack, suite
        self.name = 'binpacking'
        self.cases = [c['items'] for c in suite(50000+seed, cases)]
        self._pack, self._mutate = pack, mutate
        self.reference = sum(pack(c, BEST_FIT) for c in self.cases)/cases

    def random(self, rng): return tuple(rng.uniform(-3, 3) for _ in range(12))
    def score(self, w): return sum(self._pack(c, list(w)) for c in self.cases)/len(self.cases)
    def edit(self, w, rng): return tuple(self._mutate(list(w), rng))

    def rewrite(self, w, rng):
        out = list(w)
        for j in rng.sample(range(12), 6): out[j] = rng.uniform(-3, 3)
        return tuple(out)

    def crossover(self, a, b, rng): return tuple(x if rng.random() < .5 else y for x, y in zip(a, b))
    def display(self, score): return score-self.reference


BENCHMARKS = {
    'labs': lambda seed: LABS(40),
    'heilbronn': lambda seed: Heilbronn(12),
    'nk': lambda seed: NK(48, 6, seed),
    'binpacking': lambda seed: BinPacking(seed),
}
