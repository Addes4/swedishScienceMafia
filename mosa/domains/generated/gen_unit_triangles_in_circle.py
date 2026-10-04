import math
import numpy as np
from scipy.optimize import minimize
import mpmath as mp
from mosa.domain import Domain

KNOWN = {}
Q = 1.0 / math.sqrt(3.0)
MARGIN = 1e-7


def offsets(theta):
    a = theta[:, None] + np.arange(3)[None, :] * (2 * math.pi / 3)
    return Q * np.stack((np.cos(a), np.sin(a)), axis=-1)


def radius(c, u):
    return float(np.linalg.norm(c[:, None, :] + u, axis=2).max())


def pair_data(u):
    n = len(u)
    ii, jj = np.triu_indices(n, 1)
    edges = np.roll(u, -1, axis=1) - u
    normals = np.stack((-edges[..., 1], edges[..., 0]), axis=-1)
    normals /= np.linalg.norm(normals, axis=2)[..., None]
    axes = np.concatenate((normals[ii], normals[jj]), axis=1)
    axes = np.concatenate((axes, -axes), axis=1)
    # For each directed axis, separation is (c_j-c_i).axis - h.
    ai = np.einsum('pvd,pad->pav', u[ii], axes).max(axis=2)
    bj = np.einsum('pvd,pad->pav', u[jj], axes).min(axis=2)
    return ii, jj, axes, ai - bj


class Problem(Domain):
    family = 'unit equilateral triangles'
    title = 'Unit equilateral triangles in the smallest circle'
    problem = ('For each integer n from 108 through 131, place n equilateral '
               'triangles of side length exactly 1 in an origin-centered closed '
               'disk. Each centroid and orientation is independent. Minimize '
               'the disk radius R subject to disjoint triangle interiors; '
               'edge and vertex contact are allowed. Orientations are radians.')
    evidence = ('Erich Friedman, Triangles in Circles, '
                'https://erich-friedman.github.io/packing/triincir/, explicitly '
                'uses side-1 equilateral triangles and container radius r. '
                'The inspected page provides illustrated reference packings '
                'for n=1..50, but no entries for 108..131; no verified published '
                'values or coordinate configurations for the requested range '
                'were obtained, so KNOWN is empty. Its smallest-known wording '
                'describes records, not a general optimality theorem. Circle '
                'packing records cannot be substituted for triangle records. '
                'The area lower bound is sqrt(n*sqrt(3)/(4*pi)). This harness '
                'produces numerical feasible upper bounds, not proofs of '
                'global optimality. Verification uses separating axes and '
                '80-digit arithmetic near contact, without accepting negative '
                'residuals through a feasibility tolerance; it is numerical '
                'verification rather than a formal interval certificate.')
    api = '''def initialize(record, neighbours, rng, count):
    Return count (x, value) candidates for global integer n. record is always
    None. neighbours maps nearby m to (x, value), and may be empty.
    x is a flat float array of length 3*n+1: the first 3*n entries reshape
    to (n,3), whose rows are centroid_x, centroid_y, orientation_radians;
    x[-1] is the claimed disk radius R. value must equal R. Unit side length
    is implicit and cannot be changed. Overlapping starts are allowed.
    When using neighbours, add/remove rows and recompute a containing R.
def vary(parents, rng, count):
    Return count candidates in the same format from parent (x,value) pairs.
    Perturb translations and orientations, mix compatible parents, or use
    lattice motifs. relax optimizes translations and R at fixed input
    orientations; orientation exploration is the strategy's responsibility.
    relax repairs overlap without changing triangle side lengths.
'''
    same = 1e-7

    def targets(self):
        return list(range(108, 132))

    def reference(self, n):
        return None, KNOWN.get(n)

    def best_known(self, n):
        return KNOWN.get(n)

    def validate(self, x, value, n):
        if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or not 1 <= n <= 131:
            raise ValueError('n must be an integer in 1..131')
        try:
            raw = np.asarray(x)
            if np.iscomplexobj(raw):
                raise ValueError('complex coordinates')
            a = np.asarray(x, dtype=float)
            v = float(value)
        except (TypeError, ValueError, OverflowError) as e:
            raise ValueError('invalid numeric candidate') from e
        if a.shape != (3*n+1,) or not np.isfinite(a).all() or not math.isfinite(v):
            raise ValueError('wrong shape or nonfinite candidate')
        if np.max(np.abs(a)) > 1e4 or a[-1] < 0 or v < 0:
            raise ValueError('candidate outside numerical bounds')
        if abs(v-a[-1]) > 1e-10 * max(1.0, v, a[-1]):
            raise ValueError('value must match encoded R')
        return a.copy()

    def random(self, n, rng):
        r = math.sqrt(n * math.sqrt(3)/(4*math.pi))
        angle = rng.uniform(0, 2*math.pi, n)
        d = r * np.sqrt(rng.uniform(0, 1, n))
        c = np.column_stack((d*np.cos(angle), d*np.sin(angle)))
        t = rng.uniform(-math.pi, math.pi, n)
        R = radius(c, offsets(t)) + MARGIN
        return np.r_[np.column_stack((c, t)).ravel(), R], R

    def relax(self, x, value):
        raw = np.asarray(x)
        if raw.ndim != 1 or (raw.size-1) % 3:
            raise ValueError('wrong shape')
        n = (raw.size-1)//3
        a = self.validate(x, value, n)
        rows = a[:-1].reshape(n, 3).copy()
        rows[:, 2] = (rows[:, 2]+math.pi) % (2*math.pi)-math.pi
        u = offsets(rows[:, 2])
        ii, jj, axes, h = pair_data(u)
        c0 = rows[:, :2].copy()
        c0 -= c0.mean(axis=0)
        z = np.r_[c0.ravel(), radius(c0, u)]
        evaluations = 0

        def objective(z, weight):
            nonlocal evaluations
            evaluations += 1
            c = z[:-1].reshape(n, 2)
            R = z[-1]
            g = np.zeros((n, 2))
            gaps = np.einsum('pd,pad->pa', c[jj]-c[ii], axes)-h
            k = gaps.argmax(axis=1)
            gap = gaps[np.arange(len(ii)), k]
            p = np.maximum(MARGIN-gap, 0)
            force = (2*weight*p)[:, None]*axes[np.arange(len(ii)), k]
            np.add.at(g, ii, force)
            np.add.at(g, jj, -force)
            vertices = c[:, None, :]+u
            d = np.linalg.norm(vertices, axis=2)
            excess = np.maximum(d-R+MARGIN, 0)
            g += (2*weight*excess[..., None]*vertices/np.maximum(d[..., None], 1e-30)).sum(axis=1)
            cost = R+weight*(np.dot(p, p)+np.sum(excess*excess))
            gradR = 1-2*weight*excess.sum()
            return float(cost), np.r_[g.ravel(), gradR]

        for weight in (20.0, 200.0):
            result = minimize(objective, z, args=(weight,), jac=True,
                              method='L-BFGS-B',
                              bounds=[(-100, 100)]*(2*n)+[(0, 200)],
                              options={'maxiter': 45, 'maxls': 12, 'ftol': 1e-9})
            if np.isfinite(result.x).all():
                z = result.x
        c = z[:-1].reshape(n, 2).copy()
        c -= c.mean(axis=0)
        # Every directed support difference h is positive because the
        # centroid lies inside each triangle. Uniformly scaling CENTERS
        # makes a chosen positive center projection exceed h. Shapes stay unit.
        projections = np.einsum('pd,pad->pa', c[jj]-c[ii], axes)
        ratios = np.where(projections > 1e-12,
                          (h+MARGIN)/np.maximum(projections, 1e-12), np.inf)
        needed = ratios.min(axis=1)
        scale = max(1.0, float(needed.max())) if len(needed) else 1.0
        if not math.isfinite(scale) or scale > 5:
            # Deterministic, strictly separated fallback for coincidences
            # or badly tangled starts. Circumdisks themselves are disjoint.
            w = int(math.ceil(math.sqrt(n)))
            c = np.array([(i % w, i//w) for i in range(n)], dtype=float)
            c *= 2*Q + 10*MARGIN
            c -= c.mean(axis=0)
        else:
            c *= scale*(1+1e-9)
        rows[:, :2] = c
        R = radius(c, u)+MARGIN
        out = np.r_[rows.ravel(), R]
        return out, R, evaluations

    def polish(self, x, value):
        return x, value

    def verify(self, x, n):
        # Independent vertex construction and SAT, never pair_data/relax.
        try:
            raw = np.asarray(x)
            if raw.shape != (3*n+1,):
                raise ValueError('wrong shape')
            a = self.validate(x, raw[-1], n)
        except (TypeError, ValueError, OverflowError) as e:
            return {'valid': False, 'value': None, 'reason': str(e)}
        rows = a[:-1].reshape(n, 3)
        R = float(a[-1])
        vertices = []
        for cx, cy, t in rows:
            vertices.append(np.array([[cx+math.cos(t+k*2*math.pi/3)/math.sqrt(3),
                                       cy+math.sin(t+k*2*math.pi/3)/math.sqrt(3)]
                                      for k in range(3)]))
        vertices = np.asarray(vertices)
        enclosing = float(np.linalg.norm(vertices, axis=2).max())
        minimum_gap = math.inf
        valid = True
        # Conservative uncertainty band at the admitted coordinate scale.
        band = 1e-8
        with mp.workdps(80):
            cache = {}
            def precise(i):
                if i not in cache:
                    cx, cy, t = [mp.mpf(float(v)) for v in rows[i]]
                    q = 1/mp.sqrt(3)
                    cache[i] = [(cx+q*mp.cos(t+k*2*mp.pi/3),
                                 cy+q*mp.sin(t+k*2*mp.pi/3)) for k in range(3)]
                return cache[i]

            containment = enclosing-R
            if containment > band:
                valid = False
            elif containment >= -band:
                exact_radius = max(mp.sqrt(vx*vx+vy*vy)
                                   for i in range(n) for vx, vy in precise(i))
                containment = float(exact_radius-mp.mpf(R))
                enclosing = float(exact_radius)
                if exact_radius > mp.mpf(R):
                    valid = False
            for i in range(n):
                for j in range(i+1, n):
                    # Unit triangles lie in circumdisks of radius 1/sqrt(3).
                    distance = math.hypot(*(rows[j, :2]-rows[i, :2]))
                    if distance > 2*Q+band:
                        minimum_gap = min(minimum_gap, distance-2*Q)
                        continue
                    gap = -math.inf
                    for tri in (vertices[i], vertices[j]):
                        for k in range(3):
                            edge = tri[(k+1)%3]-tri[k]
                            axis = np.array([-edge[1], edge[0]])
                            axis /= np.linalg.norm(axis)
                            p = vertices[i]@axis
                            q = vertices[j]@axis
                            gap = max(gap, float(q.min()-p.max()), float(p.min()-q.max()))
                    if abs(gap) <= band:
                        ptri, qtri = precise(i), precise(j)
                        exact_gap = -mp.inf
                        for tri in (ptri, qtri):
                            for k in range(3):
                                dx = tri[(k+1)%3][0]-tri[k][0]
                                dy = tri[(k+1)%3][1]-tri[k][1]
                                nx, ny = -dy, dx
                                norm = mp.sqrt(nx*nx+ny*ny)
                                p = [(vx*nx+vy*ny)/norm for vx, vy in ptri]
                                q = [(vx*nx+vy*ny)/norm for vx, vy in qtri]
                                exact_gap = max(exact_gap, min(q)-max(p), min(p)-max(q))
                        gap = float(exact_gap)
                        if exact_gap < 0:
                            valid = False
                    elif gap < 0:
                        valid = False
                    minimum_gap = min(minimum_gap, gap)
        return {'valid': bool(valid), 'value': enclosing,
                'claimed_radius': R, 'enclosing_radius': enclosing,
                'containment_residual': containment,
                'overlap_residual': max(0.0, -minimum_gap),
                'minimum_separation_lower_bound': None if n == 1 else minimum_gap,
                'area_lower_bound': math.sqrt(n*math.sqrt(3)/(4*math.pi))}

    def svg(self, x, value):
        n = (np.asarray(x).size-1)//3
        a = self.validate(x, value, n)
        rows = a[:-1].reshape(n, 3)
        v = rows[:, None, :2]+offsets(rows[:, 2])
        R = max(float(value), radius(rows[:, :2], offsets(rows[:, 2])))
        extent = R+0.1
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-extent} {-extent} {2*extent} {2*extent}">',
                 f'<circle cx="0" cy="0" r="{value}" fill="white" stroke="black" stroke-width="0.02"/>']
        for tri in v:
            points = ' '.join(f'{px:.12g},{py:.12g}' for px, py in tri)
            parts.append(f'<polygon points="{points}" style="fill:#B2B2B2;stroke:black;stroke-width:0.015"/>')
        return ''.join(parts)+'</svg>'
