"""Where the waste sits: the open-bin inventory at the switch and at the end (tuning seeds only).

Usage: python experiments/online-beyond-ss-v1/mechanism.py   (writes mechanism.json; about 10 s)
Uses verify.items_for seeds 90000-90199 (5,000 items, C = 100), the tuning set, never a test set.
Waste at the end = total open gap, since every unit of gap in a used bin is waste.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fast import pack_fss  # noqa: E402
from sim import weibull_items  # noqa: E402

C, BANDS = 100, [(1, 9), (10, 29), (30, 49), (50, 99)]
cfg = json.loads((HERE / "config.json").read_text())


def bands(N):
    g = np.arange(C + 1)
    return {f"gap {a}-{b}": float((g * N)[a:b + 1].sum()) for a, b in BANDS} | {"open bins": float(N[1:C].sum())}


def main():
    variants = {"SS": (0.0, 0.0), "FWSS-no-finish": (cfg["beta"], 0.0), "SS+finish": (0.0, cfg["c"]), "FWSS": (cfg["beta"], cfg["c"])}
    out = {}
    for name, (beta, c) in variants.items():
        end, at_switch, sw_left = [], [], []
        for seed in range(90000, 90200):
            items = weibull_items(seed, 5000)
            b, N, t_sw = pack_fss(items, C, beta, c, 0.0, return_state=True)
            end.append(bands(N))
            if c > 0 and t_sw:
                _, Ns, _ = pack_fss(items[:t_sw - 1], C, beta, 0.0, 0.0, return_state=True)
                at_switch.append(bands(Ns))
                sw_left.append(5000 - t_sw + 1)
        mean = lambda rows: {k: round(float(np.mean([r[k] for r in rows])), 1) for k in rows[0]}
        out[name] = {"end": mean(end)}
        if at_switch:
            out[name]["at_switch"] = mean(at_switch)
            out[name]["items_left_at_switch"] = round(float(np.mean(sw_left)), 1)
        print(name, json.dumps(out[name]))
    (HERE / "mechanism.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
