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
    if name == "thomson":
        from .domains.thomson import Thomson
        return Thomson()
    raise ValueError(f"unknown domain {name!r}")
