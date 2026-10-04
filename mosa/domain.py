"""What Mosa needs from a problem.

A domain is a family of minimization problems indexed by an integer size n (squares in a square: n squares, minimize
the side). A candidate is (x, value): a numpy array in the domain's own format and its objective value. The domain
supplies the trusted parts of the loop, which model-written code never touches:

- targets(), reference(n), best_known(n), info(n): the instances and the best known solutions to beat;
- validate(x, value, n): reject malformed candidates from model-written code (raise ValueError);
- relax(x, value): a fast local optimizer from any candidate (overlaps allowed) to a feasible solution;
- polish(x, value): an exact local refinement of a feasible solution;
- verify(x, n): an independent, high-precision certificate (nothing is called a record without one);
- svg(x, value): a picture for the workbench.

and the text the researcher sees: problem (one paragraph), evidence (measured facts about the landscape), and api (the
signatures of initialize and vary in the domain's terms). Objective values closer than `same` are one basin.
"""
from __future__ import annotations


class Domain:
    name = ""
    family = ""  # problems in one family share a representation: one strategy can run on all of them
    title = ""
    problem = ""
    evidence = ""
    api = ""
    same = 1e-5

    def targets(self):
        raise NotImplementedError

    def reference(self, n):
        raise NotImplementedError

    def best_known(self, n):
        raise NotImplementedError

    def info(self, n):
        return {}

    def validate(self, x, value, n):
        raise NotImplementedError

    def relax(self, x, value):
        raise NotImplementedError

    def polish(self, x, value):
        return x, value

    def verify(self, x, n):
        raise NotImplementedError

    def svg(self, x, value):
        raise NotImplementedError


def get(name):
    if name == "squares":
        from .domains.squares import Squares
        return Squares()
    if name.startswith("gen-"):  # drafted on the spot by the research agent (mosa/harness.py)
        from .harness import load
        return load(name)
    if name == "thomson" or name.startswith("riesz-"):
        from .domains.thomson import Riesz
        return Riesz(1. if name == "thomson" else float(name.split("-", 1)[1]))
    raise ValueError(f"unknown problem {name!r}")


# The problem library: what the research agent can choose from. Problems in one family share a representation, so one
# strategy can run on all of them and a workspace may hold instances of several.
LIBRARY = [
    {"name": "squares", "family": "unit squares", "title": "Unit squares in the smallest square",
     "about": "Pack n unit squares, free to rotate, in the smallest square. Best known values for n up to 324 (Friedman and Ellsworth's catalogue).",
     "sizes": "non-trivial n between 5 and 324"},
    {"name": "thomson", "family": "points on a sphere", "title": "Charges on a sphere (the Thomson problem)",
     "about": "n unit charges on a sphere minimizing the Coulomb energy (sum of 1/r). Best known energies for n = 10-972 (Cambridge Cluster Database).",
     "sizes": "10-972"},
    {"name": "riesz-<s>", "family": "points on a sphere", "title": "Riesz s-energy on the sphere, for any s > 0",
     "about": "As the Thomson problem with the sum of 1/r^s. No published values for most s: nothing to memorize, so methods are compared with each other.",
     "sizes": "any n from 10 to 1000"},
]


def library():
    """The built-in problems and those drafted on the spot."""
    from .harness import library as drafted
    return LIBRARY+[{**e, "sizes": "see the harness", "drafted": True} for e in drafted()]
