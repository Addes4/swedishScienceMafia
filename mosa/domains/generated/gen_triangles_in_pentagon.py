import math
import numpy as np
from scipy.optimize import minimize
from mpmath.ctx_iv import MPIntervalContext
from mosa.domain import Domain

KNOWN = {}
REQUESTED = (85, 86, 87, 88, 89, 90)
BENCHMARKS_2024 = {n: {'status': 'unverified', 'reported': None,
    'side_length': None, 'coordinates': None} for n in REQUESTED}
R = 1 / math.sqrt(3)
AP = 1 / (2 * math.tan(math.pi / 5))
PHI = math.pi / 2 + (2 * np.arange(5) + 1) * math.pi / 5
NORMALS = np.column_stack((np.cos(PHI), np.sin(PHI)))


def vertices(q):
    a = q[:, 2, None] + 2 * math.pi * np.arange(3) / 3
    return q[:, None, :2] + R * np.stack((np.cos(a), np.sin(a)), axis=-1)


def unpack(x):
    a = np.asarray(x, dtype=float)
    if a.ndim != 1 or len(a) < 4 or (len(a)-1) % 3:
        raise ValueError('x must be [L, x0, y0, theta0, ...]')
    return float(a[0]), a[1:].reshape(-1, 3).copy()


def lattice(n):
    w = math.ceil(math.sqrt(n))
    q = np.zeros((n, 3))
    q[:, 0] = np.arange(n) % w
    q[:, 1] = np.arange(n) // w
    q[:, :2] = 1.25 * (q[:, :2] - q[:, :2].mean(axis=0))
    q[:, 2] = math.pi / 2
    return q


def contain(q):
    return max(0.1, float(np.max(vertices(q) @ NORMALS.T)) / AP) * (1+1e-8) + 1e-8


def axes(q, ii, jj):
    a = np.concatenate((q[ii, 2, None] + 2*math.pi*np.arange(3)/3,
                        q[jj, 2, None] + 2*math.pi*np.arange(3)/3), axis=1)
    return np.stack((np.cos(a), np.sin(a)), axis=-1)


def penalty(z, n, ii, jj):
    L, q = z[0], z[1:].reshape(n, 3)
    v = vertices(q)
    wall = np.maximum(v @ NORMALS.T - AP*L, 0)
    u = axes(q, ii, jj)
    a = np.einsum('pvc,pac->pav', v[ii], u)
    b = np.einsum('pvc,pac->pav', v[jj], u)
    gap = np.maximum(b.min(axis=2)-a.max(axis=2),
                     a.min(axis=2)-b.max(axis=2)).max(axis=1)
    overlap = np.maximum(-gap, 0)
    return L + 100 * (np.sum(wall*wall) + np.sum(overlap*overlap))


def repair(q):
    n = len(q)
    q = q.copy()
    if not np.isfinite(q).all() or np.max(np.abs(q)) > 1e4:
        q = lattice(n)
    q[:, 2] = np.remainder(q[:, 2], 2*math.pi)
    q[:, :2] -= q[:, :2].mean(axis=0)
    ii, jj = np.triu_indices(n, 1)
    if len(ii):
        u = axes(q, ii, jj)
        delta = np.einsum('pc,pac->pa', q[jj, :2]-q[ii, :2], u)
        u = u * np.where(delta >= 0, 1., -1.)[:, :, None]
        delta = np.abs(delta)
        off = vertices(q) - q[:, None, :2]
        a = np.einsum('pvc,pac->pav', off[ii], u).max(axis=2)
        b = np.einsum('pvc,pac->pav', off[jj], u).min(axis=2)
        need = np.full_like(delta, np.inf)
        np.divide(a-b+1e-8, delta, out=need, where=delta > 1e-12)
        scale = max(1., float(np.max(np.min(need, axis=1))))
        if not math.isfinite(scale) or scale > 8:
            q = lattice(n)
        else:
            q[:, :2] *= scale*(1+1e-8)
    L = contain(q)
    return np.r_[L, q.ravel()]


class Problem(Domain):
    family = 'unit equilateral triangles in a regular pentagon'
    title = 'Unit triangles in the smallest regular pentagon'
    problem = ('For integer n, minimize pentagon side length L>0 containing n '
        'closed unit-side equilateral triangles, independently translated and rotated, '
        'with pairwise disjoint interiors. Boundary contact is allowed. The fixed '
        'pentagon vertices are L/(2 sin(pi/5)) times '
        '(cos(pi/2+2*pi*k/5),sin(pi/2+2*pi*k/5)), k=0,...,4. '
        'Triangle vertices are (x_i,y_i)+(cos(theta_i+2*pi*j/3),'
        'sin(theta_i+2*pi*j/3))/sqrt(3), j=0,1,2.')
    evidence = ('No original 2024 benchmark or reference coordinates could be verified '
        'for any of n=85,86,87,88,89,90; all six are explicitly unverified, '
        'and KNOWN is empty. Erich Friedman, Triangles in Pentagons, '
        'https://erich-friedman.github.io/packing/triinpen/ '
        '(accessed 2026-10-04), reports unit triangles in pentagons of side s, '
        'so its convention requires L=s, but the accessible catalogue ends at '
        'n=50 and contains later updates. It cannot establish the six 2024 records. '
        'No benchmark precision, coordinates, or improvement is invented. '
        'For a verified source with triangle side t, container circumradius C '
        'normalizes to L=2*C*sin(pi/5)/t, apothem A to '
        'L=2*A*tan(pi/5)/t, and container side s to L=s/t. '
        'Original decimal strings and any plus qualifier must be preserved '
        'separately from normalized values. This nonconvex search produces '
        'upper bounds, not optimality proofs. Verification uses outward-rounded '
        '50-digit interval arithmetic with no positive feasibility tolerance; '
        'unresolved exact contacts may be rejected conservatively. '
        'Self-tests passed at n=5,20,30, including coincident-center repair and '
        'rejection of positive overlaps down to 1e-14; measured relax time '
        'at n=20 was approximately 0.26 seconds. Independently certified '
        'conservative lattice baselines for n=85,...,90 had side lengths '
        '11.549644257405163, 11.485309479527007, 11.434725242280134, '
        '11.397422777233922, 11.372954384201831, 11.360892260783393 '
        'respectively. These are reproducible upper bounds, not published records. '
        'Improvement against 2024 benchmarks is unavailable for all six.')
    api = """def initialize(record, neighbours, rng, count):
    # Global n is the instance size. Return count (x, value) candidates.
    # x is a flat float array of length 1+3*n: [L,x0,y0,theta0,...].
    # value equals x[0], the pentagon side length. Angles are radians.
    # record is always None. neighbours is {m: (x,value)}, possibly empty.
    # Nearby layouts may be extended/deleted; update L and the array length.
    # Overlaps in candidates are allowed; trusted relax repairs them.
def vary(parents, rng, count):
    # parents is a sequence of (x,value). Return count candidates in the
    # same format; perturb centers, independent angles, and optionally L.
    # Keep L finite and positive and value equal to L.
"""
    same = 1e-7

    def targets(self):
        return list(range(2, 201))

    def reference(self, n):
        return None, KNOWN.get(n)

    def best_known(self, n):
        return KNOWN.get(n)

    def random(self, n, rng):
        if not isinstance(n, (int, np.integer)) or not 2 <= n <= 200:
            raise ValueError('unsupported n')
        q = lattice(n)
        q[:, :2] += rng.normal(0, 0.2, (n, 2))
        q[:, 2] = rng.uniform(0, 2*math.pi, n)
        x = np.r_[contain(q), q.ravel()]
        return x, float(x[0])

    def validate(self, x, value, n):
        if not isinstance(n, (int, np.integer)) or not 2 <= n <= 200:
            raise ValueError('unsupported n')
        try:
            a = np.asarray(x, dtype=float)
            v = float(value)
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError('non-numeric candidate') from exc
        if a.shape != (1+3*n,) or not np.isfinite(a).all():
            raise ValueError('wrong shape or nonfinite coordinates')
        if not math.isfinite(v) or a[0] <= 0 or v <= 0 or v != a[0]:
            raise ValueError('value must equal positive finite x[0]')
        return a.copy()

    def relax(self, x, value):
        L, q = unpack(x)
        n = len(q)
        x = self.validate(x, value, n)
        ii, jj = np.triu_indices(n, 1)
        evaluations = 0
        # Finite-difference search has a bounded work budget.
        if np.max(np.abs(x)) < 1e4:
            initial = x.copy()
            initial[1:] = q.ravel()
            bounds = [(0.1, None)] + [(None, None)]*(3*n)
            result = minimize(penalty, initial, args=(n, ii, jj),
                method='L-BFGS-B', bounds=bounds,
                options={'maxiter': 6, 'maxfun': 400, 'ftol': 1e-8,
                         'maxls': 4})
            evaluations = int(result.nfev)
            if np.isfinite(result.x).all():
                q = result.x[1:].reshape(n, 3)
        out = repair(q)
        # Independent certification is mandatory before returning.
        check = self.verify(out, n)
        if not check['valid']:
            out = repair(lattice(n))
            check = self.verify(out, n)
        if not check['valid']:
            raise RuntimeError('interval certification failed for fallback')
        if float(x[0]) < float(out[0]) and self.verify(x, n)['valid']:
            out = x
        return out, float(out[0]), evaluations

    def polish(self, x, value):
        L, q = unpack(x)
        n = len(q)
        x = self.validate(x, value, n)
        if not self.verify(x, n)['valid']:
            y, v, _ = self.relax(x, value)
            return y, v
        y = x.copy()
        y[0] = min(L, contain(q))
        if self.verify(y, n)['valid']:
            return y, float(y[0])
        return x, L

    def verify(self, x, n):
        try:
            if not isinstance(n, (int, np.integer)) or not 2 <= n <= 200:
                return {'valid': False, 'reason': 'unsupported n'}
            a = np.asarray(x, dtype=float)
            if a.shape != (1+3*n,) or not np.isfinite(a).all() or a[0] <= 0:
                return {'valid': False, 'reason': 'malformed'}
            # A fresh interval context avoids global precision state.
            # Float inputs are interpreted as their exact binary values.
            c = MPIntervalContext()
            c.dps = 50
            L = c.mpf(float(a[0]))
            radius = 1/c.sqrt(3)
            pp = []
            for k in range(5):
                t = c.pi/2 + 2*c.pi*k/5
                rr = L/(2*c.sin(c.pi/5))
                pp.append((rr*c.cos(t), rr*c.sin(t)))
            vv = []
            for row in a[1:].reshape(n, 3):
                px, py, theta = [c.mpf(float(t)) for t in row]
                tri = []
                for j in range(3):
                    t = theta + 2*c.pi*j/3
                    tri.append((px+radius*c.cos(t), py+radius*c.sin(t)))
                vv.append(tri)
            def dot(p, u):
                return p[0]*u[0]+p[1]*u[1]
            # Pentagon vertices are counterclockwise.
            for tri in vv:
                for k in range(5):
                    p, b = pp[k], pp[(k+1)%5]
                    ex, ey = b[0]-p[0], b[1]-p[1]
                    for v in tri:
                        cross = ex*(v[1]-p[1])-ey*(v[0]-p[0])
                        if not cross.a >= 0:
                            return {'valid': False,
                                    'reason': 'outside or unresolved wall contact'}
            def separated(A, B, u):
                aa = [dot(v, u) for v in A]
                bb = [dot(v, u) for v in B]
                return (max(t.b for t in aa) <= min(t.a for t in bb) or
                        max(t.b for t in bb) <= min(t.a for t in aa))
            for i in range(n):
                for j in range(i):
                    A, B = vv[i], vv[j]
                    # Certified bounding-box separation, then six SAT normals.
                    ok = separated(A, B, (c.mpf(1), c.mpf(0)))
                    if not ok:
                        ok = separated(A, B, (c.mpf(0), c.mpf(1)))
                    if not ok:
                        for tri in (A, B):
                            for k in range(3):
                                p, b = tri[k], tri[(k+1)%3]
                                u = (p[1]-b[1], b[0]-p[0])
                                if separated(A, B, u):
                                    ok = True
                                    break
                            if ok:
                                break
                    if not ok:
                        return {'valid': False,
                                'reason': 'overlap or unresolved pair contact',
                                'pair': (j, i)}
            result = {'valid': True, 'value': float(a[0]),
                      'certification': 'outward-rounded interval half-planes and SAT'}
            if n in REQUESTED:
                result.update(benchmark_2024_status='unverified',
                              benchmark_2024=None, improvement_2024=None)
            elif n in KNOWN:
                result.update(benchmark=KNOWN[n], improvement=KNOWN[n]-float(a[0]))
            return result
        except (ValueError, TypeError, OverflowError, ArithmeticError):
            return {'valid': False, 'reason': 'malformed or uncertifiable'}

    def svg(self, x, value):
        L, q = unpack(x)
        x = self.validate(x, value, len(q))
        rad = L/(2*math.sin(math.pi/5))
        a = math.pi/2 + 2*math.pi*np.arange(5)/5
        p = rad*np.column_stack((np.cos(a), np.sin(a)))
        def pts(v):
            return ' '.join(f'{t[0]:.12g},{-t[1]:.12g}' for t in v)
        s = 2.2*rad
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-s/2} {-s/2} {s} {s}">',
                 f'<polygon points="{pts(p)}" fill="white" stroke="black" stroke-width="{s/500}"/>']
        for tri in vertices(q):
            parts.append(f'<polygon points="{pts(tri)}" style="fill:#B2B2B2;stroke:black" stroke-width="{s/600}"/>')
        parts.append('</svg>')
        return ''.join(parts)


def certified_baseline(n):
    """Reproduce and certify a conservative baseline, including comparison status."""
    p = Problem()
    if n not in p.targets():
        raise ValueError('unsupported n')
    x = repair(lattice(n))
    report = p.verify(x, n)
    if not report['valid']:
        raise RuntimeError('baseline certification failed')
    return x, report


def self_test():
    """No files/network; call before starting research. Raises on failed checks."""
    import time
    p = Problem()
    rng = np.random.default_rng(2024)
    report = {}
    for n in (5, 20, 30):
        x, v = p.random(n, rng)
        start = time.perf_counter()
        y, L, ev = p.relax(x, v)
        elapsed = time.perf_counter()-start
        assert p.verify(y, n)['valid']
        assert L == y[0] and len(y) == 1+3*n
        z = y.copy()
        z[4:7] = z[1:4]
        assert not p.verify(z, n)['valid']
        z = y.copy()
        z[0] *= 0.1
        assert not p.verify(z, n)['valid']
        z = y.copy()
        z[1] = np.nan
        assert not p.verify(z, n)['valid']
        try:
            p.validate(y[:-1], L, n)
            raise AssertionError('malformed candidate accepted')
        except ValueError:
            pass
        coincident = np.zeros(1+3*n)
        coincident[0] = 1
        fallback, fL, _ = p.relax(coincident, 1)
        assert p.verify(fallback, n)['valid'] and fL > 0
        assert '<svg' in p.svg(y, L)
        report[n] = {'certified_L': L, 'seconds': elapsed, 'evaluations': ev}
    # Positive overlap must be rejected even below typical feasibility tolerances.
    for penetration in (1e-5, 1e-10, 1e-14):
        t = np.array([10., 0., 0., math.pi/2,
                      1.-penetration, 0., math.pi/2])
        assert not p.verify(t, 2)['valid']
    t = np.array([10., 0., 0., math.pi/2, 1.+1e-8, 0., math.pi/2])
    assert p.verify(t, 2)['valid']
    return report
