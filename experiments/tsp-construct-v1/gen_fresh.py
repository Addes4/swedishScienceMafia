"""Fresh test instances: instance with seed s is np.random.default_rng(s).random((n, 2)).

    python gen_fresh.py   # writes data/fresh50.npy (seeds 200000-200999), data/fresh100.npy
                          # (201000-201999) and data/fresh200.npy (202000-202199)
"""
import numpy as np

SETS = {50: range(200000, 201000), 100: range(201000, 202000), 200: range(202000, 202200)}

if __name__ == "__main__":
    for n, seeds in SETS.items():
        X = np.stack([np.random.default_rng(s).random((n, 2)) for s in seeds])
        np.save(f"data/fresh{n}.npy", X)
        print(n, X.shape)
