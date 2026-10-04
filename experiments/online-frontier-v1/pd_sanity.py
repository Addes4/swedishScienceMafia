"""Sanity check of PD-exp against Gupta & Radovanovic's Figure 3 setting: bins above OPT for SS and PD-exp on
their BW (B=9), PP (B=10) and LW (B=10) distributions, one sample path per T. Expected shape: on LW, SS's
excess grows linearly and PD-exp's sublinearly; on BW, SS stays flat."""
import json, random
import frontier as F
DISTS = {"BW B=9": (9, {2: 35/48, 3: 13/48}),
         "PP B=10": (10, {1: 1/4, 3: 1/4, 4: 1/8, 5: 1/4, 8: 1/8}),
         "LW B=10": (10, {3: 1/4, 4: 1/4, 5: 1/4, 8: 1/4})}
out = []
for name, (B, p) in DISTS.items():
    for T in (1000, 4000, 16000):
        rng = random.Random(7 + T)
        items = rng.choices(list(p), weights=list(p.values()), k=T)
        opt = F.optimum(items, B)["opt"]
        row = {"dist": name, "T": T, "OPT": opt}
        for k in ("SS", "PD-exp", "PD-exp-T", "BF"):
            row[k] = F.pack_hist(items, B, F.HIST_POLICIES[k]) - opt
        out.append(row); print(row, flush=True)
json.dump(out, open("pd_sanity.json", "w"), indent=1)
