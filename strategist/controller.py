"""Policies that choose the next research move. Adaptive learns *when* to switch strategy."""
import collections
import math
import random
import statistics

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


class AdaptiveV2(Adaptive):
    """Adaptive plus the three fixes proposed in v1's RESULTS.md, each behind an option.

    With every option at its default the policy is move-for-move identical to `Adaptive` (tested), so
    v1 stays reproducible and each fix can be switched on alone for ablations.

    (a) xo_gate: crossover must earn its place. Its success rate gets a sceptical prior (v1 gives every
        move the optimistic pooled rate (wins+.5)/(pulls+1); crossover gets wins/(pulls+1), which is 0
        before any evidence). In a context it joins the Thompson draw only when its posterior mean
        yield is at least that of the best other move there. While locked it is probed with
        probability xo_probe, which is how it can earn entry; with xo_probe=0 it is never used.
    (b) excursion: how long an excursion may stall before the leader is resumed.
        'inherit' (v1) as long as the leader had stalled when it was left (at least 1 move);
        'cap'     the same, but at most excursion_len moves;
        'fixed'   always excursion_len moves, whatever the leader's patience.
    (c) leave_test: how much evidence leaving the leader needs.
        'point'     (v1) the best posterior-mean stay yield is below the explore rate;
        'improving' also require that the leader has gone `window` moves without improving
                    (a recent-improvement test: a leader that is still improving is not left);
        'yield'     also require the leader line's realised yield over its last `window` moves to be
                    below the explore rate;
        'upper'     require the upper `quantile` credible bound of the stay yield to be below it.
    """
    EXCURSION = ('inherit', 'cap', 'fixed')
    LEAVE = ('point', 'improving', 'yield', 'upper')

    def __init__(self, costs, seed, xo_gate=False, xo_probe=0., excursion='inherit', excursion_len=64,
                 leave_test='point', window=64, quantile=.9, rng_key=None, name='adaptive_v2', **kw):
        super().__init__(costs, seed, name=name, **kw)
        if rng_key is not None: self.rng = random.Random(f'{seed}/policy/{rng_key}')
        assert excursion in self.EXCURSION and leave_test in self.LEAVE, (excursion, leave_test)
        self.xo_gate, self.xo_probe = xo_gate, xo_probe
        self.excursion, self.excursion_len = excursion, max(int(excursion_len), 1)
        self.leave_test, self.window, self.quantile = leave_test, int(window), quantile
        self.z = statistics.NormalDist().inv_cdf(quantile)
        self.history = {}                 # line -> deque of recent (cost, local gain) on that line
        self.line, self.keep = None, ()   # line of the move being chosen; lines whose history is kept

    def estimates(self, state):
        est = super().estimates(state)
        if not self.xo_gate or 'crossover' not in est: return est
        key = self.key(state)
        group = [r for k, r in self.cells.items() if k.split('/')[0] == key.split('/')[0]]
        pulls, wins, gains = (sum(r['crossover'][i] for r in group) for i in range(3))
        all_wins = sum(r[op][1] for r in group for op in self.moves)
        all_gains = sum(r[op][2] for r in group for op in self.moves)
        overall_gain = all_gains/all_wins if all_wins else 1.
        rate, op_gain = wins/(pulls+1.), (gains+overall_gain)/(wins+1.)
        p, s, g, _ = self.row(key)['crossover']
        est['crossover'] = (max(s+self.prior*rate, 1e-9), max(p-s, 0.)+self.prior*(1-rate), (g+op_gain)/(s+1.),
                            self.costs['crossover'])
        return est

    def eligible(self, est):
        """Moves allowed into the Thompson draw in this context."""
        if not self.xo_gate or 'crossover' not in est: return list(est)
        mean = {op: a/(a+b)*gain/cost for op, (a, b, gain, cost) in est.items()}
        others = [op for op in est if op != 'crossover']
        if others and mean['crossover'] < max(mean[op] for op in others): return others
        return list(est)

    def recent_yield(self, line):
        h = self.history.get(line)
        if not h: return math.inf                       # no evidence yet: this test does not say leave
        cost = sum(c for c, _ in h)
        return sum(g for _, g in h)/cost if cost else math.inf

    def excursion_patience(self, run):
        inherited = max(run.leader_stall, 1)
        if self.excursion == 'cap': return min(inherited, self.excursion_len)
        if self.excursion == 'fixed': return self.excursion_len
        return inherited

    def upper_stay_rate(self, est):
        def upper(a, b): return min(1., a/(a+b)+self.z*math.sqrt(a*b/((a+b)**2*(a+b+1))))
        return max(upper(a, b)*gain/cost for a, b, gain, cost in est.values())

    def leaves(self, state, run):
        if not run.leader: return 'resume' if run.stall >= self.excursion_patience(run) else None
        est, explore = self.estimates(state), self.explore_rate(run)
        if self.leave_test == 'upper': return 'restart' if self.upper_stay_rate(est) < explore else None
        if self.stay_rate(est) >= explore: return None
        if self.leave_test == 'improving' and run.stall < self.window: return None
        if self.leave_test == 'yield' and self.recent_yield(run.line) >= explore: return None
        return 'restart'

    def choose(self, state, run):
        self.line, self.keep = run.line, (run.line, run.leader_line)
        switch = self.leaves(state, run)
        if switch: return switch
        est = self.estimates(state)
        allowed = self.eligible(est)
        if self.xo_probe and 'crossover' in est and 'crossover' not in allowed \
                and self.rng.random() < self.xo_probe:
            return 'crossover'
        best, choice = -1., None
        for op in allowed:
            a, b, gain, cost = est[op]
            value = self.rng.betavariate(a, b)*gain/cost
            if value > best: best, choice = value, op
        return choice

    def update(self, state, op, cost, gain):
        super().update(state, op, cost, gain)
        if self.leave_test == 'yield':
            self.history.setdefault(self.line, collections.deque(maxlen=self.window)).append((cost, gain))
            for line in [l for l in self.history if l not in self.keep]: del self.history[line]

    def explain(self, state, run):
        out = super().explain(state, run)
        est = self.estimates(state)
        out['eligible'] = self.eligible(est)
        if self.leave_test == 'upper': out['stay_upper'] = self.upper_stay_rate(est)
        if self.leave_test == 'yield': out['recent'] = self.recent_yield(run.line)
        if not run.leader: out['excursion_patience'] = self.excursion_patience(run)
        return out
