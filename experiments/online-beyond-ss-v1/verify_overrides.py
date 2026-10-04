"""Verify the optimum overrides in opt_overrides.json (CPU only, under a second).

An override replaces an OPT value that this study's own arc-flow solve did not prove. For each one, a
complete packing is checked: it must use exactly the instance's items (as a multiset), no bin may exceed
the capacity, and the number of bins must equal L1 = ceil(sum / C), which proves it optimal.

    python experiments/online-beyond-ss-v1/verify_overrides.py
"""
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def orlib_instance(name):
    i = {"u120": 1, "u250": 2, "u500": 3, "u1000": 4}[name.split("_")[0]]
    t = (HERE / "orlib_data" / f"binpack{i}.txt").read_text().split()
    n, k = int(t[0]), 1
    for _ in range(n):
        nm, cap, m, best = t[k], int(float(t[k + 1])), int(t[k + 2]), int(t[k + 3])
        k += 4
        items = [int(float(x)) for x in t[k:k + m]]
        k += m
        if nm == name:
            return cap, items, best
    raise KeyError(name)


def main():
    overrides = json.loads((HERE / "opt_overrides.json").read_text())
    for name, ov in overrides.items():
        cap, items, listed = orlib_instance(name)
        packing = json.loads((HERE / ov["packing_file"]).read_text())["packing"]
        assert Counter(x for b in packing for x in b) == Counter(items), f"{name}: items differ"
        assert all(sum(b) <= cap for b in packing), f"{name}: a bin exceeds capacity"
        l1 = math.ceil(sum(items) / cap)
        assert len(packing) == l1 == ov["opt"], f"{name}: {len(packing)} bins, L1 {l1}, override {ov['opt']}"
        print(f"{name}: packing verified, {len(packing)} bins = L1 -> OPT = {ov['opt']} (OR-Library lists {listed})")


if __name__ == "__main__":
    main()
