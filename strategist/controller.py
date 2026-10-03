"""Policies that choose the next research move. Adaptive learns *when* to switch strategy."""
import math
import random

OPS = ('edit', 'rewrite', 'crossover', 'restart')
WITHIN = ('edit', 'rewrite', 'crossover')       # moves that continue the current line of work
# Log-spaced stall buckets: number of consecutive non-improving moves on the working line.
STALL_EDGES = (1, 4, 16, 64, 256)
STALL_NAMES = ('fresh', 'warm', 'slowing', 'stuck', 'stagnant', 'frozen')


def context(stall, leader):
    """The only progress signal policies see: leader line or excursion, and how long it has stalled."""
    return f"{'lead' if leader else 'trail'}/{STALL_NAMES[sum(stall >= e for e in STALL_EDGES)]}"


class Policy:
    name = 'policy'

    def choose(self, state, run): raise NotImplementedError     # return an op, or None to stop
    def update(self, state, op, cost, gain): pass                # outcome of a move within the line
    def excursion_done(self, overall, cost, now): pass           # an excursion ended: its progress and cost


class Adaptive(Policy):
    """Learns when to change research strategy.

    The search keeps a leader line (it holds the best solution) and makes excursions (restarts).
    * Leave the leader for a fresh excursion when the leader's expected yield falls below the
      overall progress per cost that past excursions delivered (the marginal value theorem).
    * An excursion that has stalled as long as the leader had when it was left is equally exhausted:
      resume the leader, which then faces the same test again.
    Expected yield = max over moves of P(improves) x typical gain / cost in the current context
    (stall length x leader or excursion). Within a line, moves are chosen by Thompson sampling on the
    same quantity. Statistics decay so the policy tracks a search whose landscape keeps changing.
    """

    def __init__(self, costs, seed, moves=WITHIN, contextual=True, discount=.99, prior=4.,
                 memory=500., prior_cost=100., name='adaptive'):
        self.costs, self.moves, self.contextual, self.name = costs, tuple(moves), contextual, name
        self.discount, self.prior, self.memory, self.prior_cost = discount, prior, memory, prior_cost
        self.rng = random.Random(f'{seed}/policy/{name}')
        self.cells = {}               # context -> move -> [pulls, successes, gain_sum, cost_sum], all decayed
        self.excursions = [0., 0., 0.]  # completed excursions: [overall progress, cost, when], decayed

    def key(self, state): return state if self.contextual else state.split('/')[0]

    def row(self, key): return self.cells.setdefault(key, {op: [0., 0., 0., 0.] for op in self.moves})

    def estimates(self, state):
        """Per-move posterior in this context: (alpha, beta, gain, cost)."""
        key = self.key(state)
        group = [r for k, r in self.cells.items() if k.split('/')[0] == key.split('/')[0]]
        pulls = {op: sum(r[op][0] for r in group) for op in self.moves}
        wins = {op: sum(r[op][1] for r in group) for op in self.moves}
        gains = {op: sum(r[op][2] for r in group) for op in self.moves}
        overall_gain = sum(gains.values())/sum(wins.values()) if sum(wins.values()) else 1.
        out, row = {}, self.row(key)
        for op in self.moves:
            rate = (wins[op]+.5)/(pulls[op]+1.)
            op_gain = (gains[op]+overall_gain)/(wins[op]+1.)
            p, s, g, _ = row[op]
            out[op] = (s+self.prior*rate, max(p-s, 0.)+self.prior*(1-rate), (g+op_gain)/(s+1.), self.costs[op])
        return out

    def stay_rate(self, estimates):
        return max(a/(a+b)*gain/cost for a, b, gain, cost in estimates.values())

    def recall(self, now):
        """Excursion statistics, forgotten exponentially in cost spent, so pessimism cannot lock in."""
        overall, cost, when = self.excursions
        fade = math.exp(-(now-when)/self.memory)
        return overall*fade, cost*fade

    def explore_rate(self, run):
        """Overall progress per cost of past excursions, with the run's average progress rate as prior."""
        overall, cost = self.recall(run.spent)
        return (overall+run.progress_rate()*self.prior_cost)/(cost+self.prior_cost)

    def leaves(self, state, run):
        """The deterministic switching rule: 'restart', 'resume', or None to stay on the line."""
        if run.leader:
            return 'restart' if self.stay_rate(self.estimates(state)) < self.explore_rate(run) else None
        return 'resume' if run.stall >= max(run.leader_stall, 1) else None

    def choose(self, state, run):
        switch = self.leaves(state, run)
        if switch: return switch
        est = self.estimates(state)
        best, choice = -1., None
        for op, (a, b, gain, cost) in est.items():
            value = self.rng.betavariate(a, b)*gain/cost
            if value > best: best, choice = value, op
        return choice

    def update(self, state, op, cost, gain):
        row = self.row(self.key(state))
        for cell in row.values():
            for i in range(4): cell[i] *= self.discount
        cell = row[op]
        cell[0] += 1; cell[3] += cost
        if gain > 0: cell[1] += 1; cell[2] += gain

    def excursion_done(self, overall, cost, now):
        past_overall, past_cost = self.recall(now)
        self.excursions = [past_overall+overall, past_cost+cost, now]

    def explain(self, state, run):
        """Posterior means behind the decision, for logs and the demo."""
        est = self.estimates(state)
        return {'moves': {op: {'p_improve': a/(a+b), 'gain': gain, 'cost': cost, 'yield': a/(a+b)*gain/cost}
                          for op, (a, b, gain, cost) in est.items()},
                'stay': self.stay_rate(est), 'explore': self.explore_rate(run)}


class Fixed(Policy):
    """Draws moves from a fixed distribution, ignoring progress."""
    def __init__(self, weights, seed, name):
        self.weights, self.name = [weights.get(op, 0.) for op in OPS], name
        self.rng = random.Random(f'{seed}/policy/{name}')

    def choose(self, state, run): return self.rng.choices(OPS, self.weights)[0]


class Patience(Policy):
    """Hand-written switching rule: small edits until the line stalls for T moves, then restart."""
    def __init__(self, patience):
        self.patience, self.name = patience, f'patience_{patience}'

    def choose(self, state, run): return 'restart' if run.stall >= self.patience else 'edit'


class Replay(Policy):
    """Plays a fixed move sequence; used for the timing-shuffled control."""
    def __init__(self, ops, name='replay'):
        self.ops, self.i, self.name = list(ops), 0, name

    def choose(self, state, run):
        if self.i >= len(self.ops): return None
        self.i += 1
        return self.ops[self.i-1]


def shuffled(ops, seed):
    """Same moves in the same quantities, but at random times."""
    ops = list(ops)
    random.Random(f'{seed}/shuffle').shuffle(ops)
    return Replay(ops, 'timing_shuffled')
