"""Check that the C packer reproduces sim.py exactly (bins and final histogram)."""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from sim import pack, best_fit, sum_of_squares, weibull_items
from fast import pack_wss, wpow


def make(w, K):
    def rule(N, s, C, t, T, hist):
        if t > T - K:
            return best_fit(N, s, C, t, T, hist)
        best, best_g = None, C
        for g in range(s, C + 1):
            if g < C and not N[g]:
                continue
            r = g - s
            d = (w[g] * (-2 * N[g] + 1) if g < C else 0) + (w[r] * (2 * N[r] + 1) if r > 0 else 0)
            if best is None or (d, r) < best:
                best, best_g = (d, r), g
        return best_g
    return rule


if __name__ == "__main__":
    C = 100
    n_ok = 0
    for seed in range(97000, 97006):
        items = weibull_items(seed, 3000)
        for w, K in [([1.0] * (C + 1), 0), (wpow(1, C), 40), (wpow(2, C), 40), (wpow(2.5, C), 0)]:
            b_py, N_py = pack(items, C, make(w, K), True)
            b_c, N_c = pack_wss(items, C, w, K, True)
            assert b_py == b_c and list(N_c) == N_py, (seed, K, b_py, b_c)
            n_ok += 1
        assert pack(items, C, sum_of_squares) == pack_wss(items, C, [1.0] * (C + 1), 0)
    print(f"C packer matches sim.py on {n_ok} (instance, policy) pairs")
