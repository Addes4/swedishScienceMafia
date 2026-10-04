"""The patience restart rule used by the lean arm's optional --patience flag.

Moved here from strategist/controller.py when the Strategist component was removed from main (its studies and code
are in tag archive/full-research-2026-10-04). Behaviour is unchanged.
"""
STALL_EDGES = (1, 4, 16, 64, 256)
STALL_NAMES = ('fresh', 'warm', 'slowing', 'stuck', 'stagnant', 'frozen')


def context(stall, leader):
    """The only progress signal a policy sees: leader line or excursion, and how long it has stalled."""
    return f"{'lead' if leader else 'trail'}/{STALL_NAMES[sum(stall >= e for e in STALL_EDGES)]}"


class Patience:
    """Hand-written switching rule: small edits until the line stalls for T moves, then restart."""
    def __init__(self, patience):
        self.patience, self.name = patience, f'patience_{patience}'

    def choose(self, state, run): return 'restart' if run.stall >= self.patience else 'edit'
