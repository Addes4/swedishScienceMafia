import math
import sys
import time


def solve(n):
    sys.setrecursionlimit(10000)
    t0 = time.time()
    total_budget = 40.0
    k0 = max(1, math.isqrt(n))
    if k0 * k0 < n:
        k0 += 1
    # start from the plain grid
    kg = math.isqrt(n)
    best_ratio = float(kg) * (1.0 / kg) * kg / kg * kg  # = kg * (1/kg) * ... (placeholder)
    best_ratio = kg * (1.0 / kg)  # sum of sides of the kg x kg grid = kg
    best_ratio = float(kg)
    best_sol = [((i + 0.5) / kg, (j + 0.5) / kg, 0.0, 1.0 / kg)
                for i in range(kg) for j in range(kg)]

    kmax = max(k0, int(math.ceil(3 * math.sqrt(n))))
    ks = list(range(max(1, kg), kmax + 1))

    for idx, k in enumerate(ks):
        now = time.time()
        remaining = total_budget - (now - t0)
        if remaining <= 0.2:
            break
        deadline = now + remaining / (len(ks) - idx)
        h = [0] * k
        stack = []
        state = {"best": best_ratio * k, "sol": None, "cnt": 0, "stop": False}
        kk = k * k

        def rec(cur, used, area_filled):
            if state["stop"]:
                return
            state["cnt"] += 1
            if (state["cnt"] & 1023) == 0 and time.time() > deadline:
                state["stop"] = True
                return
            if cur > state["best"] + 1e-9:
                state["best"] = cur
                state["sol"] = list(stack)
            p = n - used
            if p <= 0 or area_filled >= kk:
                return
            A = kk - area_filled
            if cur + math.sqrt(p * A) <= state["best"] + 1e-9:
                return
            # lowest leftmost column
            c = 0
            m = h[0]
            for i in range(1, k):
                if h[i] < m:
                    m = h[i]
                    c = i
            w = 1
            while c + w < k and h[c + w] == m:
                w += 1
            smax = min(w, k - m)
            for s in range(smax, 0, -1):
                for i in range(c, c + s):
                    h[i] += s
                stack.append((c, m, s))
                rec(cur + s, used + 1, area_filled + s * s)
                stack.pop()
                for i in range(c, c + s):
                    h[i] -= s
                if state["stop"]:
                    return
            # leave this cell empty
            h[c] += 1
            rec(cur, used, area_filled + 1)
            h[c] -= 1

        rec(0, 0, 0)
        if state["sol"] is not None and state["best"] / k > best_ratio + 1e-12:
            best_ratio = state["best"] / k
            best_sol = [((x + s / 2.0) / k, (y + s / 2.0) / k, 0.0, s / float(k))
                        for (x, y, s) in state["sol"]]

    res = list(best_sol)[:n]
    res += [(0.5, 0.5, 0.0, 0.0)] * (n - len(res))
    return res
