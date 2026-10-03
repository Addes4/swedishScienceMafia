# EVOLVE-BLOCK-START
"""Pack n squares by physical relaxation: grow when feasible, push apart when not."""
import math
import random


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    def overlap(sq):
        m = len(sq)
        for i in range(m):
            ax, ay, a = sq[i]
            ra = a / 2.0
            for j in range(i + 1, m):
                bx, by, b = sq[j]
                r = ra + b / 2.0 - 1e-12
                if abs(bx - ax) < r and abs(by - ay) < r:
                    return True
        return False

    def clamp(sq):
        for s in sq:
            h = s[2] / 2.0
            s[0] = min(max(s[0], h), 1.0 - h)
            s[1] = min(max(s[1], h), 1.0 - h)

    best_sum = -1.0
    best = None
    k0 = math.ceil(math.sqrt(n))

    for trial in range(7):
        random.seed((n * 7919 + trial) & 0x7FFFFFFF)
        sq = []
        for i in range(n):
            r = i // k0
            c = i % k0
            base = 1.0 / (k0 + 0.2)
            sq.append([
                (c + 0.5) / k0 + random.uniform(-0.06, 0.06),
                (r + 0.5) / k0 + random.uniform(-0.06, 0.06),
                base * random.uniform(0.75, 1.0),
            ])
        clamp(sq)

        for it in range(2500):
            if not overlap(sq):
                tot = sum(s[2] for s in sq)
                if tot > best_sum:
                    best_sum = tot
                    best = [x[:] for x in sq]
                for s in sq:
                    s[2] = min(s[2] * 1.008, 1.0)
            else:
                for _ in range(6):
                    m = len(sq)
                    for i in range(m):
                        a = sq[i]
                        for j in range(i + 1, m):
                            b = sq[j]
                            dx = b[0] - a[0]
                            dy = b[1] - a[1]
                            half = (a[2] + b[2]) / 2.0
                            ox = half - abs(dx)
                            oy = half - abs(dy)
                            if ox > 0.0 and oy > 0.0:
                                if ox < oy:
                                    p = ox / 2.0
                                    if dx >= 0:
                                        a[0] -= p
                                        b[0] += p
                                    else:
                                        a[0] += p
                                        b[0] -= p
                                else:
                                    p = oy / 2.0
                                    if dy >= 0:
                                        a[1] -= p
                                        b[1] += p
                                    else:
                                        a[1] += p
                                        b[1] -= p
                    clamp(sq)
                if overlap(sq):
                    for s in sq:
                        s[2] *= 0.99
            clamp(sq)

    if best is None:
        k = math.isqrt(n)
        side = 1.0 / k
        best = [((i % k + 0.5) * side, (i // k + 0.5) * side, side) for i in range(n)]
        best += [(0.5, 0.5, 0.0)] * (n - len(best))

    return [(x[0], x[1], 0.0, x[2]) for x in best][:n]
# EVOLVE-BLOCK-END
