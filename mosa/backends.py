"""Where the numerical work of a run happens: in the current process (local) or in Modal containers.

A backend gives a run three operations: step (run strategy code), relax (many candidates) and polish (a few basins).
Locally, each run is one process on one core and many runs share a process pool (see research.map_runs); on Modal,
runs are threads in the lab process and every operation fans out over containers.
"""
from __future__ import annotations

import math

from . import sandbox


class Local:
    name = "local"

    def __init__(self, domain):
        self.domain = domain

    def step(self, code, kind, payload, count, seed, n):
        return sandbox.step(self.domain, code, kind, payload, count, seed, n)

    def relax(self, xs, values):
        out = []
        for x, value in zip(xs, values):
            try:
                x, value, used = self.domain.relax(x, value)
                out.append({"x": x, "value": value, "used": used})
            except ValueError as error:
                out.append({"error": str(error)})
        return out

    def polish(self, packings):
        return [self.domain.polish(x, value) for x, value in packings]


class Modal:
    name = "modal"

    def __init__(self, domain):
        self.domain = domain
        from . import modal_app
        self.app = modal_app

    def step(self, code, kind, payload, count, seed, n):
        return self.app.strategy_step.remote(self.domain.name, code, kind, payload, count, seed, n)

    def relax(self, xs, values):
        cores, containers = self.app.CORES, self.app.CONTAINERS
        batch = cores*max(2, math.ceil(len(xs)/(containers*cores)))
        chunks = [(self.domain.name, xs[i:i+batch], values[i:i+batch]) for i in range(0, len(xs), batch)]
        return [r for part in self.app.relax_batch.starmap(chunks) for r in part]

    def polish(self, packings):
        size = self.app.POLISH_CORES
        chunks = [(self.domain.name, packings[i:i+size]) for i in range(0, len(packings), size)]
        return [r for part in self.app.polish_batch.starmap(chunks) for r in part]


def session(name):
    """Context that keeps one Modal app running for a whole lab (nothing to open locally)."""
    from contextlib import ExitStack, nullcontext
    if name != "modal":
        return nullcontext()
    import modal
    from .modal_app import app
    stack = ExitStack()
    stack.enter_context(modal.enable_output())
    stack.enter_context(app.run())
    return stack
