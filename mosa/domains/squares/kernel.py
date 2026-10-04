"""Compiled numerics for unit squares in a square: penalty relaxation, feasibility repair and an overlap check.

A packing is an (n, 3) array of unit-square centres and angles [x, y, theta] in the container [0, side]^2.

relax minimizes side + strength * overlap energy over a continuation of penalty strengths with an L-BFGS written in
Numba (Armijo backtracking; the side is the one bounded variable). It ends near a local optimum, only to a tolerance;
make_feasible then removes any remaining overlap by expanding centre distances and encloses the squares tightly, and
check confirms the result independently of the search energy.
"""
from __future__ import annotations

import math

import numpy as np
from numba import njit

STRENGTHS = (20., 200., 2000., 200000.)
MARGIN = 2e-10  # every pair and wall of a relaxed packing is at least this far apart


@njit(cache=True)
def _sign(x):
    return 1. if x > 0 else (-1. if x < 0 else 0.)


@njit(cache=True)
def energy_gradient(z):
    """Squared penetration depth of every overlapping pair (separating-axis depth) and wall, with its gradient;
    z = [x, y, theta] * n + [side]. Pairs with centres at least sqrt(2) apart cannot overlap and are skipped."""
    n = (len(z)-1)//3
    side = z[-1]
    grad = np.zeros_like(z)
    value = 0.
    c, s = np.empty(n), np.empty(n)
    for i in range(n):
        c[i], s[i] = math.cos(z[3*i+2]), math.sin(z[3*i+2])
    for i in range(n):
        x, y, ci, si = z[3*i], z[3*i+1], c[i], s[i]
        half = .5*(abs(ci)+abs(si))
        dh = .5*(-_sign(ci)*si+_sign(si)*ci)
        for axis in range(2):
            pos = z[3*i+axis]
            for edge in range(2):
                p = half-pos if edge == 0 else pos+half-side
                if p > 0:
                    value += p*p
                    f = 2.*p
                    grad[3*i+axis] += -f if edge == 0 else f
                    grad[3*i+2] += f*dh
                    if edge == 1:
                        grad[-1] -= f
        for j in range(i):
            dx, dy = z[3*j]-x, z[3*j+1]-y
            if dx*dx+dy*dy >= 2.:
                continue
            cj, sj = c[j], s[j]
            cd, sd = cj*ci+sj*si, sj*ci-cj*si
            support = .5*(1+abs(cd)+abs(sd))
            ds = .5*(-_sign(cd)*sd+_sign(sd)*cd)
            best, bx, by, bt_i, bt_j = -1e100, 0., 0., 0., 0.
            for a in range(4):  # edge normals of square i (a = 0, 1) and square j (a = 2, 3)
                if a == 0:
                    ux, uy = ci, si
                elif a == 1:
                    ux, uy = -si, ci
                elif a == 2:
                    ux, uy = cj, sj
                else:
                    ux, uy = -sj, cj
                dot = dx*ux+dy*uy
                gap = abs(dot)-support
                if gap > best:
                    best = gap
                    sign = _sign(dot)
                    bx, by = sign*ux, sign*uy
                    rot = sign*(-dx*uy+dy*ux)
                    bt_i = ds+(rot if a < 2 else 0.)
                    bt_j = -ds+(rot if a >= 2 else 0.)
            if best < 0:
                p = -best
                value += p*p
                f = -2.*p
                grad[3*i] -= f*bx
                grad[3*i+1] -= f*by
                grad[3*j] += f*bx
                grad[3*j+1] += f*by
                grad[3*i+2] += f*bt_i
                grad[3*j+2] += f*bt_j
    return value, grad


@njit(cache=True)
def _objective(z, strength):
    energy, gradient = energy_gradient(z)
    gradient = strength*gradient
    gradient[-1] += 1.
    return z[-1]+strength*energy, gradient


@njit(cache=True)
def _stage(w, strength, lo, hi, budget, memory, ftol, gtol):
    """Minimize one penalty stage with L-BFGS; return the best point seen and the evaluations used."""
    size = len(w)
    s_hist, y_hist, rho = np.zeros((memory, size)), np.zeros((memory, size)), np.zeros(memory)
    alpha = np.zeros(memory)
    w = w.copy()
    w[-1] = min(max(w[-1], lo), hi)
    f, g = _objective(w, strength)
    used, stored, newest = 1, 0, 0
    best_w, best_f = w.copy(), f
    while used < budget:
        pg = g.copy()
        if (w[-1] <= lo and g[-1] > 0) or (w[-1] >= hi and g[-1] < 0):
            pg[-1] = 0.
        if np.max(np.abs(pg)) <= gtol:
            break
        q = pg.copy()  # two-loop recursion over the stored curvature pairs, newest first
        for j in range(stored):
            i = (newest-1-j) % memory
            alpha[i] = rho[i]*np.dot(s_hist[i], q)
            q -= alpha[i]*y_hist[i]
        if stored:
            i = (newest-1) % memory
            q *= np.dot(s_hist[i], y_hist[i])/np.dot(y_hist[i], y_hist[i])
        else:
            q /= max(1., np.sqrt(np.dot(pg, pg)))
        for j in range(stored-1, -1, -1):
            i = (newest-1-j) % memory
            q += s_hist[i]*(alpha[i]-rho[i]*np.dot(y_hist[i], q))
        d = -q
        if pg[-1] == 0.:
            d[-1] = 0.
        slope = np.dot(g, d)
        if slope >= 0.:
            stored, d = 0, -pg
            slope = np.dot(g, d)
        step, accepted = 1., False
        while used < budget:
            trial = w+step*d
            trial[-1] = min(max(trial[-1], lo), hi)
            ft, gt = _objective(trial, strength)
            used += 1
            if ft < best_f:
                best_w, best_f = trial.copy(), ft
            if ft <= f+1e-4*step*slope:
                accepted = True
                break
            step *= .5
            if step < 1e-20:
                break
        if not accepted:
            break
        s, y = trial-w, gt-g
        sy = np.dot(s, y)
        if sy > 1e-12*np.dot(y, y):
            s_hist[newest], y_hist[newest], rho[newest] = s, y, 1./sy
            newest, stored = (newest+1) % memory, min(stored+1, memory)
        converged = abs(f-ft) <= ftol*max(abs(f), abs(ft), 1.)
        w, f, g = trial, ft, gt
        if converged:
            break
    return best_w, used


@njit(cache=True)
def _expansion(q, margin):
    """Smallest uniform scaling of centre positions that separates every pair by margin (at least 1); -1 for
    coincident centres. Pairs whose centres are more than sqrt(3) apart are already separated (their projected
    distance on some edge normal exceeds the largest support, (1 + sqrt 2)/2)."""
    scale = 1.
    n = len(q)
    for i in range(n):
        for j in range(i):
            dx, dy = q[j, 0]-q[i, 0], q[j, 1]-q[i, 1]
            if dx*dx+dy*dy >= 3.:
                continue
            t = q[j, 2]-q[i, 2]
            support = .5*(1+abs(math.cos(t))+abs(math.sin(t)))
            distance = 0.
            for a in (q[i, 2], q[i, 2]+math.pi/2, q[j, 2], q[j, 2]+math.pi/2):
                distance = max(distance, abs(dx*math.cos(a)+dy*math.sin(a)))
            if distance < 1e-12:
                return -1.
            scale = max(scale, (support+margin)/distance)
    return scale


@njit(cache=True)
def vertices(q):
    v = np.empty((len(q), 4, 2))
    for i in range(len(q)):
        c, s = math.cos(q[i, 2]), math.sin(q[i, 2])
        for k, (u, w) in enumerate(((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))):
            v[i, k, 0] = q[i, 0]+c*u-s*w
            v[i, k, 1] = q[i, 1]+s*u+c*w
    return v


@njit(cache=True)
def clearances(q, side):
    """(smallest wall clearance, smallest pair clearance) by the separating axis test; pairs whose centres are at
    least sqrt(2) apart are separated and skipped (pair clearance is inf when no pair is that close)."""
    v = vertices(q)
    wall = 1e100
    for i in range(len(q)):
        for k in range(4):
            for a in range(2):
                wall = min(wall, v[i, k, a], side-v[i, k, a])
    pair = np.inf
    for i in range(len(q)):
        for j in range(i):
            dx, dy = q[j, 0]-q[i, 0], q[j, 1]-q[i, 1]
            if dx*dx+dy*dy >= 2.:
                continue
            gap = -1e100
            for t in (q[i, 2], q[i, 2]+math.pi/2, q[j, 2], q[j, 2]+math.pi/2):
                ux, uy = math.cos(t), math.sin(t)
                lo_i, hi_i, lo_j, hi_j = 1e100, -1e100, 1e100, -1e100
                for k in range(4):
                    a = v[i, k, 0]*ux+v[i, k, 1]*uy
                    b = v[j, k, 0]*ux+v[j, k, 1]*uy
                    lo_i, hi_i, lo_j, hi_j = min(lo_i, a), max(hi_i, a), min(lo_j, b), max(hi_j, b)
                gap = max(gap, lo_i-hi_j, lo_j-hi_i)
            pair = min(pair, gap)
    return wall, pair


def check(q, side, n=None, tolerance=1e-9):
    """True when the packing is n finite squares inside [0, side]^2 with no overlap beyond tolerance."""
    q = np.asarray(q, dtype=float)
    if q.ndim != 2 or q.shape[1] != 3 or (n is not None and len(q) != n) or not np.isfinite(q).all() or not side > 0:
        return False
    wall, pair = clearances(q, float(side))
    return wall >= -tolerance and pair >= -tolerance


def make_feasible(q, side, margin=MARGIN):
    """Expand centre distances until no pair overlaps, then enclose the unchanged unit squares tightly; returns
    (poses with angles in [-pi/4, pi/4), side). No overlap is hidden by a tolerance."""
    q = np.asarray(q, dtype=float).copy()
    if not np.isfinite(q).all() or not math.isfinite(side):
        raise ValueError("non-finite candidate")
    scale = _expansion(q, margin)
    if scale < 0:
        raise ValueError("coincident centres cannot be repaired by expansion")
    q[:, :2] *= scale
    q[:, 2] = (q[:, 2]+math.pi/4) % (math.pi/2)-math.pi/4
    v = vertices(q)
    low, high = v.min(axis=(0, 1)), v.max(axis=(0, 1))
    q[:, :2] += margin-low
    return q, float(max(high-low)+2*margin)


def relax(q, side, allowance=None):
    """Relax a candidate (overlaps allowed) to a feasible packing near a local optimum: (poses, side, evaluations).
    The continuation spends the allowance (default 1000 n evaluations; typically about 350 n are used) over the
    penalty stages and stops each stage at convergence."""
    z = np.r_[np.asarray(q, dtype=float).ravel(), float(side)]
    n = len(z)//3
    allowance = allowance or 1000*n
    lo, hi = math.sqrt(n), max(side*1.5, math.ceil(math.sqrt(n))*1.5)
    used = 0
    for stage, strength in enumerate(STRENGTHS):
        if used >= allowance:
            break
        budget = max(1, (allowance-used)//(len(STRENGTHS)-stage))
        z, count = _stage(z, strength, lo, hi, budget, 15, 1e-14, 1e-8)
        used += count
    poses, side = make_feasible(z[:-1].reshape(-1, 3), float(z[-1]))
    if not check(poses, side, n, tolerance=1e-10):
        raise ValueError("the independent check rejected a relaxed packing")
    return poses, side, used
