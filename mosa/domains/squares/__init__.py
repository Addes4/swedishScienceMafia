"""Unit squares in the smallest square (the squares-in-squares catalogue of Erich Friedman and David Ellsworth).

Best known packings come from the known-best witnesses of github.com/jlevy/squares (data/squares/known-best.jsonl);
official sides and history notes from the catalogue (data/squares/catalogue.json).
"""
from __future__ import annotations

from functools import cached_property
import json
import math
from pathlib import Path

import numpy as np

from ...domain import Domain
from . import audit, kernel, polish as polishing, render

DATA = Path(__file__).resolve().parents[3]/"data"/"squares"


class Squares(Domain):
    name = "squares"
    family = "unit squares"
    title = "Unit squares in the smallest square"
    problem = ("Pack n identical unit squares, each free to translate and rotate, without overlap into the smallest "
               "square container. The objective is the container side.")
    evidence = """What we measured on this landscape (packings of n = 37-200 unit squares; every candidate is relaxed to convergence
by an L-BFGS penalty method, and the best are polished to their exact local optimum by SQP):
- Exact local optimization leaves every best known packing for n <= 200 unchanged: they are exact local optima.
- Perturbing a best known packing (moving, tilting or re-placing groups of up to 9 squares, or pushing it along its softest
  collective deformation modes) and relaxing returns the same packing or worse ones. Repeated rounds that keep the 16-32 best
  distinct results and perturb them again never improved a best known packing for n = 51-89 or 101-200.
- Relaxing random starts lands 0.02-0.15 above the best known side for n >= 39 (larger n often on plain grids). For n <= 41,
  rounds of local search from the best of 20,000 random starts do reach the best known packings.
- Removing a square from the best packing for n+1, or adding one to the best packing for n-1, and relaxing lands 0.001-0.18
  above the best known side.
- Best known packings are made of axis-aligned grid or staircase regions plus one to several domains of squares sharing a
  tilt of 15-45 degrees; recent improvements replaced single 45-degree domains by several lower-angle domains.
- A relaxed side can sit up to 1e-3 above the polished optimum of its basin; packings whose sides differ by less than 1e-5
  are treated as the same basin."""
    api = '''def initialize(record, neighbours, rng, count):
    """record: (poses, side), the best known packing for this n; poses is an (n, 3) array of [x, y, angle in radians] of
    unit-square centres in [0, side]^2. neighbours: dict {m: (poses, side)}, the best known packings for m = n-2, n-1, n+1,
    n+2 and any reference sizes named in the brief. Return up to `count` starting candidates (poses with exactly n rows,
    side); overlaps are fine: each is relaxed."""

def vary(parents, rng, count):
    """parents: list of (poses, side), the current population of distinct relaxed packings for this n, best first.
    Return `count` new candidates (exactly n squares each) derived from the population; overlaps are fine."""'''

    @cached_property
    def _witnesses(self):
        out = {}
        for line in (DATA/"known-best.jsonl").read_text().splitlines():
            row = json.loads(line)
            out[row["n"]] = (np.array(row["poses"]), float(row["side"]))
        return out

    @cached_property
    def _catalogue(self):
        return {int(k): v for k, v in json.loads((DATA/"catalogue.json").read_text()).items()}

    def targets(self):
        """Sizes whose best known side is below the trivial grid's ceil(sqrt n)."""
        return [n for n in sorted(self._witnesses) if self.best_known(n) < math.ceil(math.sqrt(n))-1e-9]

    def reference(self, n):
        poses, side = self._witnesses[n]
        if not kernel.check(poses, side+1e-6, n, tolerance=1e-6):  # low-precision witnesses may overlap below 1e-6
            raise ValueError(f"n={n}: the known-best witness fails the independent check")
        return poses.copy(), side

    def best_known(self, n):
        official = self._catalogue.get(n, {}).get("official_side")
        return min(self._witnesses[n][1], official) if official else self._witnesses[n][1]

    def info(self, n):
        entry = self._catalogue.get(n, {})
        return {"best_known": self.best_known(n), "official": entry.get("official_side"), "witness": self._witnesses[n][1],
                "closed_form": entry.get("closed_form"), "notes": entry.get("notes"), "grid": math.ceil(math.sqrt(n))}

    def validate(self, x, value, n):
        x = np.asarray(x, dtype=float)
        if x.shape != (n, 3) or not np.isfinite(x).all() or not 0 < float(value) <= 4*math.sqrt(n) or np.abs(x).max() > 1000:
            raise ValueError(f"a candidate has shape {x.shape} (expected ({n}, 3)), non-finite values or an out-of-range side")
        gaps = np.linalg.norm(x[:, None, :2]-x[None, :, :2], axis=-1)+np.eye(n)
        if gaps.min() < 1e-9:
            raise ValueError("a candidate places two squares at the same centre")
        return x

    def relax(self, x, value):
        return kernel.relax(x, value)

    def polish(self, x, value):
        return polishing.polish(x, value)

    def verify(self, x, n):
        return audit.verify(x, n, self.best_known(n))

    def svg(self, x, value):
        return render.catalogue_svg(x, value)
