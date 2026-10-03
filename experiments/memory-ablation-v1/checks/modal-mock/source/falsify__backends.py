"""Problem backends for the closed-loop memory study.

The loop in closed_loop.py only talks to a backend through this interface, so a new
regime (other instance distributions, longer instances, a code representation) is a
new class registered in BACKENDS; the loop and the memory builders do not change.

    name                       registry key, recorded in every trace
    baseline, baseline_name    reference policy (best-fit) and its display name
    system_prompt()            problem statement and representation, shown to the model
    proposal_schema()          JSON schema for one structured proposal
    parse(obj) -> policy       validated policy (JSON-serialisable dict); ValueError if invalid
    render(policy) -> str      short human-readable formula
    cases(seed, count, split)  'train' (search) or 'audit' (train + shifted families)
    evaluate(policy, cases)    list of bin counts, one per case
    pack(policy, items, trace) bin count, or (bins, assignments) when trace=True
    items(case), family(case)
    failure_shrink_executions  default greedy-deletion budget for counterexamples
"""
import math

from .contextual import CONTEXT_BEST_FIT, CONTEXT_FEATURES, PreparedCase, evaluate_cases, pack_contextual
from .core import SHIFT_FAMILIES, TRAIN_FAMILIES, suite

FEATURE_KEYS = ['w00_gap', 'w01_gap_sq', 'w02_inv_gap', 'w03_exact_fit', 'w04_gap_lt10',
                'w05_gap_lt_item', 'w06_gap_ge_item', 'w07_dist_q25', 'w08_dist_q50', 'w09_dist_q75',
                'w10_gap_lt33', 'w11_gap_lt50', 'w12_gap_x_nofit', 'w13_open_x_nofit',
                'w14_p_item_near_gap', 'w15_nearest_past_dist', 'w16_p_fit_gap', 'w17_gap_x_pfit',
                'w18_pfit_before_minus_after', 'w19_gap_x_mean_past']

FEATURE_DOCS = [
    'gap/100',
    '(gap/100)^2',
    '1/(gap+1)',
    '1 if gap == 0 else 0',
    '1 if 0 < gap < 10 else 0',
    '1 if 0 < gap < item else 0',
    '1 if gap >= item else 0',
    '|gap/100 - 0.25|',
    '|gap/100 - 0.50|',
    '|gap/100 - 0.75|',
    '1 if 0 < gap < 33 else 0',
    '1 if 0 < gap < 50 else 0',
    'gap/100 * (1 - p_fit(gap))',
    '(1 if gap > 0 else 0) * (1 - p_fit(gap))',
    'smoothed fraction of past items with size in [gap-2, gap+2]',
    'distance from gap to the nearest past item size, /100 (|gap-50.5|/100 before any item)',
    'p_fit(gap)',
    'gap/100 * p_fit(gap)',
    'p_fit(free) - p_fit(gap), where free is the space before placing the item',
    'gap/100 * mean_past_item/100',
]

SHRINK_EXECUTIONS = 2000
WEIGHT_BOUND = 12.0


class WeightsBackend:
    """20 bounded feature weights scoring each feasible bin; 80-item synthetic families.

    This is the V3/V4 regime (falsify/contextual.py and contextual.cpp), unchanged."""

    name = 'weights20_synthetic80'
    baseline_name = 'best_fit'
    failure_shrink_executions = SHRINK_EXECUTIONS

    def __init__(self):
        assert len(FEATURE_KEYS) == len(FEATURE_DOCS) == len(CONTEXT_FEATURES) == 20
        self.baseline = {'weights': list(CONTEXT_BEST_FIT)}

    def system_prompt(self):
        features = '\n'.join(f'- {k}: {d}' for k, d in zip(FEATURE_KEYS, FEATURE_DOCS))
        return f"""You are researching online one-dimensional bin-packing heuristics.

Items with integer sizes 1-100 arrive one at a time and must be placed immediately, in arrival
order, into bins of capacity 100. A fixed packer scores every open bin that can hold the item as
score = sum_j weight_j * feature_j and puts the item into the highest-scoring bin (ties go to the
lowest-index bin). A new bin is opened only when no open bin can hold the item. The policy never
sees future items. You choose the 20 weights.

Notation for one candidate bin: free = space left in the bin before the item, gap = free - item
(space left after placing it). p_fit(x) = smoothed fraction of the items seen so far in this
instance with size <= x, i.e. an estimate of how likely a future item fits into a gap of x.
mean_past_item = smoothed mean size of the items seen so far. Smoothing adds 25 pseudo-items
spread uniformly over sizes 1-100, so early estimates start near uniform.

Features, in order (weight key: feature):
{features}

Best-fit is w00_gap = -1 with all other weights 0: each item goes into the feasible bin that it
fills most tightly. All-zero weights give first-fit. Best-fit is a strong baseline and most
changes to it use more bins.

Instances have 80 items. Search instances come from five families in equal shares: uniform
(sizes 1-99), small (1-35), large (35-95), bimodal (5-20 or 65-85, equally likely) and
complementary (sizes near a and 100-a for a random a in 15-45, +/-3). The final held-out
evaluation adds three distribution-shifted families that are not described here.

Goal: a policy that uses fewer bins than best-fit on average over fresh instances.

Reply with one proposal: a short snake_case name, a one- or two-sentence hypothesis, what result
would falsify it, and all 20 weights. Every weight must be a finite number in [-12, 12]."""

    def proposal_schema(self):
        return {'type': 'object', 'additionalProperties': False,
                'required': ['name', 'hypothesis', 'falsification', 'weights'],
                'properties': {
                    'name': {'type': 'string'}, 'hypothesis': {'type': 'string'},
                    'falsification': {'type': 'string'},
                    'weights': {'type': 'object', 'additionalProperties': False, 'required': FEATURE_KEYS,
                                'properties': {k: {'type': 'number'} for k in FEATURE_KEYS}}}}

    def parse(self, obj):
        weights = obj.get('weights') if isinstance(obj, dict) else None
        if not isinstance(weights, dict) or set(weights) != set(FEATURE_KEYS):
            raise ValueError('weights must contain exactly the 20 feature keys')
        values = [weights[k] for k in FEATURE_KEYS]
        if not all(isinstance(w, (int, float)) and not isinstance(w, bool) and math.isfinite(w)
                   and abs(w) <= WEIGHT_BOUND for w in values):
            raise ValueError(f'every weight must be finite and within +/-{WEIGHT_BOUND:g}')
        return {'weights': [float(w) for w in values]}

    def render(self, policy):
        terms = [f'{k}={w:g}' for k, w in zip(FEATURE_KEYS, policy['weights']) if w != 0]
        return ', '.join(terms) if terms else 'all weights 0 (first-fit)'

    def cases(self, seed, count, split='train'):
        families = TRAIN_FAMILIES if split == 'train' else TRAIN_FAMILIES + SHIFT_FAMILIES
        return [PreparedCase(x) for x in suite(seed, count, families)]

    def evaluate(self, policy, cases):
        return evaluate_cases(cases, policy['weights'])

    def pack(self, policy, items, trace=False):
        return pack_contextual(list(items), policy['weights'], trace)

    @staticmethod
    def items(case):
        return list(case.items)

    @staticmethod
    def family(case):
        return case.family

    @property
    def train_families(self):
        return list(TRAIN_FAMILIES)

    @property
    def audit_families(self):
        return TRAIN_FAMILIES + SHIFT_FAMILIES


BACKENDS = {WeightsBackend.name: WeightsBackend}


def get_backend(name):
    if name not in BACKENDS:
        raise SystemExit(f'Unknown backend {name}; choose from {sorted(BACKENDS)}')
    return BACKENDS[name]()


def shrink_failure(backend, items, policy, budget=None):
    """Greedy single-item deletion, as in falsify/pilot.py: keep a deletion whenever the
    policy still uses more bins than the baseline. Unlike pilot.py the scan continues
    after a deletion instead of restarting at item 0, which reaches the same fixpoint
    (no single deletion preserves the failure) in far fewer executions. Repeats passes
    until a pass deletes nothing or the budget (two executions per trial) runs out.
    Not a proof of global minimality."""
    budget = backend.failure_shrink_executions if budget is None else budget
    current, executions, changed = list(items), 0, True
    while changed and executions + 2 <= budget:
        changed, i = False, 0
        while i < len(current) and executions + 2 <= budget:
            trial = current[:i] + current[i + 1:]
            executions += 2
            if backend.pack(policy, trial) > backend.pack(backend.baseline, trial):
                current, changed = trial, True
            else:
                i += 1
    return current, executions


def bins_from_assignments(items, assignments):
    bins = {}
    for item, b in zip(items, assignments):
        bins.setdefault(b, []).append(item)
    return [bins[b] for b in sorted(bins)]


def first_divergence(items, candidate_assignments, reference_assignments):
    """First arrival where the two policies chose different bins from an identical state."""
    free = []
    for k, (item, a, b) in enumerate(zip(items, candidate_assignments, reference_assignments)):
        if a != b:
            # The packer opens a bin only when none fits, so from an identical state both
            # choices are existing bins; 100 covers a new bin defensively.
            return {'index': k, 'item': item, 'candidate_free': free[a] if a < len(free) else 100,
                    'reference_free': free[b] if b < len(free) else 100}
        if a == len(free):
            free.append(100)
        free[a] -= item
    return None
