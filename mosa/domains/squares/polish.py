"""Exact local polish: shrink a feasible packing to its local optimum with SQP.

A relaxation ends near a local optimum, but only to a tolerance (its side can sit 1e-3 above the optimum of its basin).
Here every nearby pair's non-overlap is written with the separating edge it uses now (every corner of one square lies
at least 1/2 beyond the other's centre along that edge's outward normal), the walls bound every corner of the squares
that can reach them, and SLSQP minimizes the side with exact derivatives. Edges are re-chosen and the problem re-solved
until the side stops shrinking; every step is repaired and independently checked. The result is a local optimum of its
basin (a KKT point); it says nothing about other basins.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import minimize

from .kernel import check, make_feasible

CORNERS = np.array([[.5, .5], [.5, -.5], [-.5, .5], [-.5, -.5]])


def _rot(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.stack([np.stack([c, -s], -1), np.stack([s, c], -1)], -2)


def corners(q):
    """(n, 4, 2) corner positions and their derivatives with respect to each square's angle."""
    r, dr = _rot(q[:, 2]), _rot(q[:, 2]+math.pi/2)
    return q[:, None, :2]+np.einsum("nij,kj->nki", r, CORNERS), np.einsum("nij,kj->nki", dr, CORNERS)


def separating_edges(q, reach=math.sqrt(2)+.15):
    """For every pair within reach, (owner, other, k): the owner's edge normal at angle theta_owner + k pi/2 along
    which the pair is separated most (ties go to the first square of the pair and the lowest k)."""
    v = corners(q)[0]
    d = q[:, None, :2]-q[None, :, :2]
    i, j = np.nonzero(np.triu(np.hypot(d[..., 0], d[..., 1]) <= reach, 1))
    k = np.arange(4)*math.pi/2
    gaps = []
    for owner, other in ((i, j), (j, i)):
        phi = q[owner, 2][:, None]+k
        u = np.stack([np.cos(phi), np.sin(phi)], -1)
        gaps.append(np.einsum("pcd,pkd->pkc", v[other]-q[owner, None, :2], u).min(-1)-.5)
    best = np.argmax(np.concatenate(gaps, 1), 1)
    first = best < 4
    return np.stack([np.where(first, i, j), np.where(first, j, i), best % 4], 1)


def constraints(z, edges, n, walls):
    """Values (>= 0 when feasible) and exact Jacobian of the pair and wall constraints at z = [x, y, theta] * n +
    [side]. Rows: 4 per pair (one per corner of the other square), 16 per wall square (corner, axis, lower/upper)."""
    q, side = z[:-1].reshape(n, 3), z[-1]
    v, dv = corners(q)
    e = np.asarray(edges, dtype=int).reshape(-1, 3)
    owner, other = e[:, 0], e[:, 1]
    phi = q[owner, 2]+e[:, 2]*math.pi/2
    u = np.stack([np.cos(phi), np.sin(phi)], -1)
    du = np.stack([-np.sin(phi), np.cos(phi)], -1)
    rel = v[other]-q[owner, None, :2]
    w = np.asarray(walls, dtype=int)
    pairs, rows = 4*len(e), 4*len(e)+16*len(w)
    values, jac = np.empty(rows), np.zeros((rows, 3*n+1))
    r = 4*np.arange(len(e))[:, None]+np.arange(4)[None, :]
    values[:pairs] = (np.einsum("pcd,pd->pc", rel, u)-.5).ravel()
    jac[r, 3*other[:, None]] = u[:, None, 0]
    jac[r, 3*other[:, None]+1] = u[:, None, 1]
    jac[r, 3*other[:, None]+2] = np.einsum("pcd,pd->pc", dv[other], u)
    jac[r, 3*owner[:, None]] = -u[:, None, 0]
    jac[r, 3*owner[:, None]+1] = -u[:, None, 1]
    jac[r, 3*owner[:, None]+2] = np.einsum("pcd,pd->pc", rel, du)
    if len(w):
        i, c, axis, upper = (a.ravel() for a in np.meshgrid(w, np.arange(4), np.arange(2), np.arange(2), indexing="ij"))
        rr = pairs+np.arange(len(i))
        sign = np.where(upper == 1, -1., 1.)
        values[pairs:] = np.where(upper == 1, side-v[i, c, axis], v[i, c, axis])
        jac[rr, 3*i+axis] = sign
        jac[rr, 3*i+2] = sign*dv[i, c, axis]
        jac[rr, -1] = upper.astype(float)
    return values, jac


def polish(q, side, rounds=8, tolerance=1e-13):
    """Local optimum of the side from a feasible packing: (poses, side)."""
    q = np.asarray(q, dtype=float)
    n = len(q)
    z = np.r_[q.ravel(), float(side)]
    best = float(side)
    objective = np.zeros(3*n+1)
    objective[-1] = 1.
    for _ in range(rounds):
        q = z[:-1].reshape(n, 3)
        edges = separating_edges(q)
        walls = [i for i in range(n) if min(q[i, 0], q[i, 1], z[-1]-q[i, 0], z[-1]-q[i, 1]) < 1.25]  # others cannot reach a wall
        cache = {}

        def evaluated(w):  # SLSQP asks for values and Jacobian at the same point: compute both once
            key = w.tobytes()
            if key not in cache:
                cache.clear()
                cache[key] = constraints(w, edges, n, walls)
            return cache[key]
        result = minimize(lambda w: w[-1], z, jac=lambda w: objective, method="SLSQP",
                          constraints=[{"type": "ineq", "fun": lambda w: evaluated(w)[0], "jac": lambda w: evaluated(w)[1]}],
                          options={"ftol": 1e-16, "maxiter": 500})
        poses, box = make_feasible(result.x[:-1].reshape(n, 3), float(result.x[-1]))
        if not check(poses, box, n, tolerance=1e-10) or box > best:
            break  # a separating edge switched or the step left the model: keep the last checked packing
        z = np.r_[poses.ravel(), box]
        improved, best = best-box, box
        if improved < tolerance:
            break
    return z[:-1].reshape(n, 3), float(z[-1])
