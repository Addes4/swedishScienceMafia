import math
import numpy as np
from scipy.optimize import minimize
import mpmath as mp
from mosa.domain import Domain

KNOWN = {}


def _array(x, n):
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or not 20 <= n <= 25:
        raise ValueError('n must be an integer from 20 through 25')
    try:
        raw = np.asarray(x)
        if raw.dtype.kind not in 'iuf':
            raise ValueError('coordinates must be real numbers')
        p = np.array(raw, dtype=float, copy=True)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('invalid coordinates') from exc
    if p.shape != (n, 2) or not np.isfinite(p).all():
        raise ValueError('expected a finite array of shape (n, 2)')
    if np.max(np.abs(p)) > 1e100:
        raise ValueError('coordinate magnitude exceeds supported numerical range')
    return p


def _radius(p):
    # Compute from the actual binary floats and round the radius upwards.
    with mp.workdps(80):
        extent = max(mp.sqrt(mp.mpf(float(a))**2 + mp.mpf(float(b))**2)
                     for a, b in p) + 1
        r = float(extent)
        if mp.mpf(r) < extent:
            r = math.nextafter(r, math.inf)
        return math.nextafter(r, math.inf)


def _lattice(n):
    # A deterministic emergency packing with comfortably separated centers.
    k = math.ceil(math.sqrt(n))
    p = np.array([(2.1 * (col + 0.5 * (row % 2)),
                   2.1 * math.sqrt(3) * row / 2)
                  for row in range(k) for col in range(k)], dtype=float)[:n]
    return p - p.mean(axis=0)


def _repair(p):
    p = np.array(p, dtype=float, copy=True)
    n = len(p)
    if not np.isfinite(p).all():
        p = _lattice(n)
    else:
        scale = max(1.0, float(np.max(np.abs(p))))
        p /= scale
        p -= p.mean(axis=0)
        i, j = np.triu_indices(n, 1)
        d = np.linalg.norm(p[i] - p[j], axis=1)
        closest = float(d.min())
        # Near-coincident centers would require a numerically unstable scale.
        if closest < 1e-8:
            p = _lattice(n)
        else:
            p *= (2.0 * (1.0 + 1e-10)) / closest
    return p, _radius(p)


class Problem(Domain):
    family = 'unit circles in a circle'
    title = 'Smallest circle enclosing unit circles'
    problem = ('For each integer n from 20 through 25, place n circles of radius 1 '
               'with centers x_i in R^2 inside an enclosing circle centered at the '
               'origin. Minimize its radius R subject to every pairwise center '
               'distance being at least 2 and every center satisfying ||x_i|| + 1 '
               '<= R. Translation allows the enclosing center to be fixed without '
               'loss of generality. The objective is recomputed from the centers.')
    evidence = ('Packomania maintains published best-known equal-circle packings '
                'in a circle: https://www.packomania.com/cci/ . Its normalization '
                'uses small-circle radius rho inside a unit container; the '
                'corresponding enclosing radius here is R = 1/rho. Best-known '
                'packings should not be interpreted as proofs of global optimality. '
                'KNOWN is deliberately empty because no numerical records have '
                'been transcribed and checked. Local optimization is heuristic '
                'and does not certify a global minimum.')
    api = '''def initialize(record, neighbours, rng, count):
    Return count candidates, each (x, value), where x is a finite real numpy
    array of shape (n, 2) containing the unit-circle centers and value is a
    finite positive proposed enclosing radius. Overlaps and an undersized
    proposed radius are allowed: the trusted harness repairs candidates and
    recomputes their radius. The global integer n is the current size, in
    {20,21,22,23,24,25}. record is always None; no coordinates are stored.
    neighbours is {m: (x, value)}, containing best solutions found for nearby
    sizes, possibly empty. Adapt a neighbour by adding or removing centers.
    rng is a numpy random generator. Do not modify neighbour arrays in place.

def vary(parents, rng, count):
    Return count candidates in the same (x, value) format by perturbing or
    recombining parent candidates of the current size n. parents contains
    (x, value) pairs. Copy arrays before modifying them. Overlaps are allowed.
'''
    same = 1e-7

    def targets(self):
        return list(range(20, 26))

    def reference(self, n):
        return None, KNOWN.get(n)

    def best_known(self, n):
        return KNOWN.get(n)

    def random(self, n, rng):
        _array(np.zeros((n, 2)), n)
        angles = rng.uniform(0.0, 2.0 * math.pi, size=n)
        radii = math.sqrt(n) * np.sqrt(rng.uniform(0.0, 1.0, size=n))
        p = np.column_stack((radii * np.cos(angles), radii * np.sin(angles)))
        return p, _radius(p)

    def validate(self, x, value, n):
        p = _array(x, n)
        try:
            v = np.asarray(value)
            if v.shape != () or v.dtype.kind not in 'iuf':
                raise ValueError('radius must be a real scalar')
            r = float(v)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError('invalid radius') from exc
        if not math.isfinite(r) or r < 1.0 or r > 1e100:
            raise ValueError('radius must be finite and between 1 and 1e100')
        return p

    def relax(self, x, value):
        try:
            n = len(x)
        except TypeError as exc:
            raise ValueError('expected a center array') from exc
        p = self.validate(x, value, n)
        original = p.copy()
        best, best_r = _repair(p)
        # Normalize extreme inputs before the bounded-cost local search.
        p /= max(1.0, float(np.max(np.abs(p))))
        p -= p.mean(axis=0)
        p *= math.sqrt(n) / max(float(np.linalg.norm(p, axis=1).max()), 1e-12)
        i, j = np.triu_indices(n, 1)
        if np.min(np.linalg.norm(p[i] - p[j], axis=1)) < 1e-8:
            # Deterministic asymmetry lets coincident candidates leave a zero-gradient state.
            t = np.arange(n, dtype=float)
            p += 0.05 * np.column_stack((np.cos(2.399963229728653 * t),
                                        np.sin(2.399963229728653 * t)))
        z = np.r_[p.ravel(), np.linalg.norm(p, axis=1).max()]
        evaluations = 0

        def objective(z, weight):
            nonlocal evaluations
            evaluations += 1
            centers = z[:-1].reshape(n, 2)
            extent = z[-1]
            delta = centers[i] - centers[j]
            distances = np.sqrt(np.sum(delta * delta, axis=1) + 1e-24)
            overlap = np.maximum(2.0 - distances, 0.0)
            norms = np.sqrt(np.sum(centers * centers, axis=1) + 1e-24)
            excess = np.maximum(norms - extent, 0.0)
            gradient = np.zeros_like(centers)
            pair_gradient = (-2.0 * weight * overlap / distances)[:, None] * delta
            np.add.at(gradient, i, pair_gradient)
            np.add.at(gradient, j, -pair_gradient)
            gradient += (2.0 * weight * excess / norms)[:, None] * centers
            cost = extent + weight * (overlap @ overlap + excess @ excess)
            return float(cost), np.r_[gradient.ravel(), 1.0 - 2.0 * weight * excess.sum()]

        try:
            for weight in (100.0, 10000.0):
                result = minimize(objective, z, args=(weight,), jac=True,
                                  method='L-BFGS-B',
                                  bounds=[(None, None)] * (2 * n) + [(0.0, None)],
                                  options={'maxiter': 100, 'maxfun': 400,
                                           'maxls': 20, 'ftol': 1e-10})
                if not np.isfinite(result.x).all():
                    break
                z = result.x
                candidate, radius = _repair(z[:-1].reshape(n, 2))
                if radius < best_r:
                    best, best_r = candidate, radius
        except (ValueError, FloatingPointError, OverflowError):
            pass
        # Preserve already-feasible input when it beats the repaired search result.
        checked = self.verify(original, n)
        if checked['valid'] and checked['value'] < best_r:
            best, best_r = original, checked['value']
        # Independent strict check guards even against floating-point repair failure.
        checked = self.verify(best, n)
        if not checked['valid']:
            best = _lattice(n)
            checked = self.verify(best, n)
        if not checked['valid']:
            raise RuntimeError('internal fallback packing failed verification')
        return best, checked['value'], evaluations

    def polish(self, x, value):
        n = len(x)
        p = self.validate(x, value, n)
        checked = self.verify(p, n)
        if not checked['valid']:
            raise ValueError('polish requires a feasible packing')
        return p, checked['value']

    def verify(self, x, n):
        try:
            p = _array(x, n)
        except ValueError as exc:
            return {'valid': False, 'reason': str(exc)}
        # Independent arithmetic on the supplied floats, without overlap tolerances.
        with mp.workdps(80):
            points = [(mp.mpf(float(a)), mp.mpf(float(b))) for a, b in p]
            for i in range(n):
                for j in range(i):
                    dx = points[i][0] - points[j][0]
                    dy = points[i][1] - points[j][1]
                    if dx * dx + dy * dy < 4:
                        return {'valid': False, 'reason': 'overlap between circles %d and %d' % (j, i)}
            required = max(mp.sqrt(a * a + b * b) + 1 for a, b in points)
            radius = float(required)
            if mp.mpf(radius) < required:
                radius = math.nextafter(radius, math.inf)
            radius = math.nextafter(radius, math.inf)
            container = mp.mpf(radius)
            for a, b in points:
                if mp.sqrt(a * a + b * b) + 1 > container:
                    return {'valid': False, 'reason': 'containment failure'}
        return {'valid': True, 'value': radius}

    def svg(self, x, value):
        p = self.validate(x, value, len(x))
        checked = self.verify(p, len(p))
        if not checked['valid']:
            raise ValueError('cannot draw an infeasible packing')
        radius = checked['value']
        margin = 0.05 * radius
        side = 2.0 * (radius + margin)
        parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.17g %.17g %.17g %.17g">' %
                 (-radius - margin, -radius - margin, side, side),
                 '<circle cx="0" cy="0" r="%.17g" style="fill:white;stroke:black;stroke-width:0.04"/>' % radius]
        for a, b in p:
            parts.append('<circle cx="%.17g" cy="%.17g" r="1" style="fill:#B2B2B2;stroke:black;stroke-width:0.025"/>' % (a, b))
        parts.append('</svg>')
        return ''.join(parts)
