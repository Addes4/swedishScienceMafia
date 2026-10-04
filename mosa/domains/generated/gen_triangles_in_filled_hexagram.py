import math
import numpy as np
import mpmath as mp
from scipy.optimize import minimize
from mosa.domain import Domain

KNOWN = {}
_S = math.sqrt(3.0)
_BASE = np.array([[0., 1./_S], [-.5, -1./(2*_S)], [.5, -1./(2*_S)]])
_NORMALS = np.array([[0., -1.], [_S/2, .5], [-_S/2, .5]])


def _vertices(p):
    c, s = np.cos(p[:, 2]), np.sin(p[:, 2])
    v = np.empty((len(p), 3, 2))
    v[:, :, 0] = p[:, 0, None] + c[:, None]*_BASE[:, 0] - s[:, None]*_BASE[:, 1]
    v[:, :, 1] = p[:, 1, None] + s[:, None]*_BASE[:, 0] + c[:, None]*_BASE[:, 1]
    return v


def _axes(v):
    e = np.roll(v, -1, axis=1)-v
    return np.stack((-e[:, :, 1], e[:, :, 0]), axis=-1)


def _pair_data(p):
    v = _vertices(p)
    i, j = np.triu_indices(len(p), 1)
    a = _axes(v)
    axes = np.concatenate((a[i], a[j]), axis=1)
    u = v-p[:, None, :2]
    pi = np.einsum('pkd,pad->pka', u[i], axes)
    pj = np.einsum('pkd,pad->pka', u[j], axes)
    d = np.einsum('pd,pad->pa', p[j, :2]-p[i, :2], axes)
    # Either projection ordering can supply a separating axis.
    need = np.where(d >= 0, pi.max(1)-pj.min(1), pj.max(1)-pi.min(1))
    return np.abs(d), need


def _enclosing(p):
    projections = _vertices(p) @ _NORMALS.T
    h = np.minimum(projections.max(axis=(1, 2)), (-projections).max(axis=(1, 2)))
    return max(1.e-6, float(h.max())*2*_S)


def _repair(p):
    p = p.copy()
    p[:, 2] = np.remainder(p[:, 2], 2*math.pi/3)
    p[:, :2] -= p[:, :2].mean(axis=0)
    d, need = _pair_data(p)
    if len(d):
        ratios = np.full_like(d, np.inf)
        np.divide(need, d, out=ratios, where=d > 1.e-12)
        factor = max(1., float(ratios.min(axis=1).max()))
        if not math.isfinite(factor) or factor > 1.e5:
            return None
        p[:, :2] *= factor*(1+1.e-8)
    L = _enclosing(p)*(1+1.e-8)+1.e-8
    return np.r_[p.ravel(), L], L


def _lattice(n):
    # A side-3k hexagram contains exactly 12k^2 unit lattice cells.
    k = int(math.ceil(math.sqrt(n/12.)))
    L = 3.*k
    cells = []
    def point(i, j):
        return np.array([i+j/2., j*_S/2.])
    for j in range(-2*k-1, 2*k+1):
        for i in range(-3*k-1, 3*k+1):
            for ids in (((i,j),(i+1,j),(i,j+1)),
                        ((i+1,j),(i+1,j+1),(i,j+1))):
                v = np.array([point(*a) for a in ids])
                z = v @ _NORMALS.T
                if min(z.max(), (-z).max()) <= L/(2*_S)+1.e-10:
                    center = v.mean(axis=0)
                    angle = math.atan2(v[0,1]-center[1], v[0,0]-center[0])-math.pi/2
                    cells.append([center[0], center[1], angle])
    cells.sort(key=lambda p: p[0]*p[0]+p[1]*p[1])
    if len(cells) < n:
        raise RuntimeError('Lattice construction failed')
    return _repair(np.array(cells[:n]))


class Problem(Domain):
    family = 'unit equilateral triangles'
    title = 'Unit triangles in a filled Star of David'
    problem = ('For integer n, place n closed equilateral triangles of side one, each with an independent translation and rotation, in T(L) union -T(L), minimizing L>0. T(L) has vertices (0,L/sqrt(3)), (-L/2,-L/(2sqrt(3))), and (L/2,-L/(2sqrt(3))). Both constituent triangles have circumcenter zero and relative rotation pi. The central hexagon is filled. Boundary contact is allowed, but triangle interiors must be pairwise disjoint and every triangle must lie in the nonconvex union. Return feasible upper bounds, not claims of optimality.')
    evidence = ('No verified published best-known packing for this exact formulation at n=85 through 90 was identified; KNOWN is intentionally empty and no record claim is made. The related paper Packing and Covering a Unit Equilateral Triangle with Equilateral Triangles, Electronic Journal of Combinatorics 12 (2005), R55, https://www.combinatorics.org/ojs/index.php/eljc/article/view/v12i1r55 concerns a different container and supplies no comparable hexagram baseline. An elementary triangular-lattice construction tiles a side-3k filled hexagram with 12k^2 unit triangles. This harness adds numerical clearance, giving L<9.000001 for each n=85,...,90. These are constructive bounds, not published best values. For future comparisons: outer circumradius R gives L=sqrt(3)R; star boundary-segment length a gives L=3a; container area A gives L=sqrt(sqrt(3)A); unit-container constituent side with packed triangle side s gives L=1/s. Area alone gives L>=sqrt(sqrt(3)*n/4).')
    api = '''def initialize(record, neighbours, rng, count):
    Return count (x, value) candidates. The global n is the number of triangles.
    x is a flat float array of length 3*n+1: consecutive (cx,cy,theta)
    triples, then L. Angles are radians; centers are Cartesian coordinates.
    value must equal x[-1]. Overlaps are permitted before relaxation.
    record is always None. neighbours is {m: (x,value)}, possibly empty;
    insert or remove complete triples when transferring nearby solutions.
def vary(parents, rng, count):
    Return count candidates in the same format by changing centers, angles,
    and/or L. Every orientation is allowed. Feasibility and the objective
    are independently recomputed from x; a claimed value cannot override L.
'''
    same = 1.e-7

    def targets(self):
        return list(range(2, 201))

    def reference(self, n):
        return None, KNOWN.get(n)

    def best_known(self, n):
        return KNOWN.get(n)

    def validate(self, x, value, n):
        if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or not 2 <= n <= 200:
            raise ValueError('Unsupported size')
        try:
            a = np.asarray(x, dtype=float)
            value = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError('Expected real coordinates and objective') from exc
        if a.shape != (3*n+1,) or not np.isfinite(a).all():
            raise ValueError('Expected a finite flat array of length 3*n+1')
        if not math.isfinite(value) or a[-1] <= 0 or value <= 0:
            raise ValueError('L must be finite and positive')
        if abs(value-a[-1]) > 1.e-10*max(1., abs(value), abs(a[-1])):
            raise ValueError('value must equal the encoded L')
        if np.max(np.abs(a)) > 1.e6:
            raise ValueError('Candidate exceeds numerical range')
        return a.copy()

    def random(self, n, rng):
        x, L = _lattice(n)
        p = x[:-1].reshape(n, 3).copy()
        p[:, :2] += rng.normal(0., .12, (n, 2))
        p[:, 2] += rng.normal(0., .15, n)
        return np.r_[p.ravel(), L], L

    def relax(self, x, value):
        a = np.asarray(x)
        n = (a.size-1)//3
        a = self.validate(x, value, n)
        p = a[:-1].reshape(n, 3)
        fallback = _lattice(n)
        best = _repair(p)
        if best is None or best[1] > fallback[1]:
            best = fallback
        evaluations = 0
        # A bounded penalty search; repair, rather than optimizer success,
        # establishes feasibility. The containment surrogate is conservative:
        # each triangle is assigned to one of the two constituent triangles.
        def loss(z):
            nonlocal evaluations
            evaluations += 1
            q = z[:-1].reshape(n, 3)
            L = z[-1]
            d, need = _pair_data(q)
            overlap = np.maximum(0., (need-d).min(axis=1))
            h = _vertices(q) @ _NORMALS.T
            outside = np.maximum(0., np.minimum(h.max(axis=(1,2)), (-h).max(axis=(1,2)))-L/(2*_S))
            return L+80.*(overlap@overlap+outside@outside)
        try:
            result = minimize(loss, a, method='L-BFGS-B',
                              bounds=[(-1.e4,1.e4)]*(3*n)+[(.1,1.e4)],
                              options={'maxiter': 3, 'maxfun': 3*(3*n+2), 'maxls': 3, 'ftol': 1.e-7})
            if np.isfinite(result.x).all():
                repaired = _repair(result.x[:-1].reshape(n,3))
                if repaired is not None and repaired[1] < best[1]:
                    best = repaired
        except (ValueError, FloatingPointError, OverflowError):
            pass
        return best[0], best[1], evaluations

    def polish(self, x, value):
        return x, value

    def verify(self, x, n):
        try:
            raw = np.asarray(x, dtype=float)
            a = self.validate(raw, raw[-1], n)
        except (ValueError, TypeError, IndexError, OverflowError):
            return {'valid': False, 'value': None, 'reason': 'Malformed candidate'}
        # Independent 80-digit polygon clipping, with no feasibility epsilon.
        # Float inputs are interpreted as their actual binary values.
        with mp.workdps(80):
            M = mp.mpf
            root = mp.sqrt(3)
            L = M(float(a[-1]))
            base = [(M(0),1/root),(-M('.5'),-1/(2*root)),(M('.5'),-1/(2*root))]
            polys = []
            for row in a[:-1].reshape(n,3):
                cx, cy, t = map(lambda v: M(float(v)), row)
                c, s = mp.cos(t), mp.sin(t)
                polys.append([(cx+c*u-s*v,cy+s*u+c*v) for u,v in base])
            normals = [(M(0),-M(1)),(root/2,M('.5')),(-root/2,M('.5'))]
            planes_a = [(u,v,L/(2*root)) for u,v in normals]
            planes_b = [(-u,-v,L/(2*root)) for u,v in normals]
            def clip(poly, plane, inside=True):
                if not poly:
                    return []
                u,v,h = plane
                def f(p):
                    z = u*p[0]+v*p[1]-h
                    return z if inside else -z
                out = []
                prev, fp = poly[-1], f(poly[-1])
                for curr in poly:
                    fc = f(curr)
                    if (fp <= 0) != (fc <= 0):
                        t = fp/(fp-fc)
                        out.append((prev[0]+t*(curr[0]-prev[0]),prev[1]+t*(curr[1]-prev[1])))
                    if fc <= 0:
                        out.append(curr)
                    prev, fp = curr, fc
                return out
            def area(poly):
                if len(poly) < 3:
                    return M(0)
                return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[i][1]*poly[(i+1)%len(poly)][0] for i in range(len(poly))))/2
            def outside_parts(poly, planes):
                result = []
                for plane in planes:
                    piece = clip(poly, plane, False)
                    if area(piece) > 0:
                        result.append(piece)
                    poly = clip(poly, plane, True)
                    if not poly:
                        break
                return result
            for poly in polys:
                for piece in outside_parts(poly, planes_a):
                    if any(area(q) > 0 for q in outside_parts(piece, planes_b)):
                        return {'valid': False, 'value': float(L), 'reason': 'Triangle crosses the nonconvex boundary'}
            for i in range(n):
                for j in range(i):
                    # Exact separating-axis test on independently built polygons.
                    separated = False
                    for poly in (polys[i], polys[j]):
                        for k in range(3):
                            p, q = poly[k], poly[(k+1)%3]
                            u,v = -(q[1]-p[1]),q[0]-p[0]
                            pi = [u*r[0]+v*r[1] for r in polys[i]]
                            pj = [u*r[0]+v*r[1] for r in polys[j]]
                            if max(pi) <= min(pj) or max(pj) <= min(pi):
                                separated = True
                                break
                        if separated:
                            break
                    if not separated:
                        return {'valid': False, 'value': float(L), 'reason': 'Triangle interiors overlap'}
            return {'valid': True, 'value': float(L)}

    def svg(self, x, value):
        a = np.asarray(x, dtype=float)
        n = (a.size-1)//3
        a = self.validate(a, value, n)
        L = a[-1]
        R = L/_S
        boundary = []
        for k in range(12):
            angle = math.pi/2+k*math.pi/6
            r = R if k % 2 == 0 else L/3
            boundary.append((r*math.cos(angle),r*math.sin(angle)))
        def points(v):
            return ' '.join(f'{p[0]:.12g},{-p[1]:.12g}' for p in v)
        extent = 1.08*R
        result = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-extent} {-extent} {2*extent} {2*extent}">',
                  f'<polygon points="{points(boundary)}" fill="white" stroke="black" stroke-width="{L/500}"/>']
        for v in _vertices(a[:-1].reshape(n,3)):
            result.append(f'<polygon points="{points(v)}" style="fill:#B2B2B2;stroke:black" stroke-width="{L/900}"/>')
        result.append('</svg>')
        return ''.join(result)
