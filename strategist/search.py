"""One research run: a working line of solutions, an archive of line bests, and a policy choosing moves.

Every candidate costs one evaluation plus a generation charge that grows with the size of the move,
a proxy for an LLM writing a diff, a crossover of two programs, or a full program. A restart opens an
excursion: a fresh line that either overtakes the leader line or is abandoned. `resume` abandons the
current excursion and returns to the leader line; it evaluates nothing and is free.
"""
import copy
import math
import random
from .controller import context

COSTS = {'edit': 1.2, 'crossover': 1.5, 'rewrite': 2.0, 'restart': 2.0, 'resume': 0.}
UNIFORM_COSTS = {'edit': 1., 'crossover': 1., 'rewrite': 1., 'restart': 1., 'resume': 0.}
ARCHIVE_LINES = 8


def improvement(before, after):
    """Scale-free size of an improvement: log-ratio when both scores share a sign, else relative."""
    if before*after > 0: return abs(math.log(after/before))
    return (before-after)/max(abs(before), 1e-12)


class Run:
    def __init__(self, problem, policy, budget, seed, costs=COSTS, stream=0, trace=False):
        self.problem, self.policy, self.budget, self.seed, self.costs = problem, policy, budget, seed, costs
        self.rng = random.Random(f'{seed}/{stream}/moves')
        start = problem.random(random.Random(f'{seed}/init'))      # identical start for every policy
        self.working = self.best = start
        self.f_start = self.f_work = self.f_best = problem.score(start)
        self.spent = self.line_cost = costs['restart']              # the initial draw is charged as a restart
        self.stall = self.steps = self.line = self.leader_line = self.leader_stall = 0
        self.archive = {0: (self.f_work, start)}                   # best solution of each recent line
        self.ops, self.usage = [], {}
        self.curve = [(self.spent, self.f_best)]                    # best-so-far, recorded on improvement
        self.trace = [] if trace else None

    @property
    def leader(self): return self.line == self.leader_line

    def progress_rate(self):
        """Overall progress per cost unit so far: the run's average yield."""
        return improvement(self.f_start, self.f_best)/self.spent if self.f_best < self.f_start else 0.

    def partner(self):
        """Best of another line. Excursions never borrow from the leader, so they stay independent."""
        others = [x for line, (_, x) in self.archive.items()
                  if line != self.line and (self.leader or line != self.leader_line)]
        return self.rng.choice(others) if others else self.problem.random(self.rng)

    def step(self):
        """Apply one move. Returns False when the policy stops or the budget cannot pay for the move."""
        state = context(self.stall, self.leader)
        op = self.policy.choose(state, self)
        if op is None or self.spent+self.costs[op] > self.budget+1e-9: return False
        if op == 'resume': return self.resume()
        p, rng = self.problem, self.rng
        if op == 'edit': child = p.edit(self.working, rng)
        elif op == 'rewrite': child = p.rewrite(self.working, rng)
        elif op == 'crossover': child = p.crossover(self.working, self.partner(), rng)
        else: child = p.random(rng)
        f, cost = p.score(child), self.costs[op]
        self.spent += cost; self.steps += 1
        self.ops.append(op)
        self.usage.setdefault(state, dict.fromkeys(self.costs, 0))[op] += 1
        local = 0.
        if op == 'restart':
            if self.leader: self.leader_stall = self.stall
            else: self.end_excursion(0.)
            self.line += 1
            self.working, self.f_work, self.stall, accepted = child, f, 0, True
            self.line_cost = cost
        else:
            self.line_cost += cost
            accepted = f <= self.f_work                             # ties accepted: neutral drift
            if f < self.f_work: local = improvement(self.f_work, f)
            self.stall = 0 if f < self.f_work else self.stall+1
            if accepted: self.working, self.f_work = child, f
        if self.f_work < self.archive.get(self.line, (math.inf,))[0]:
            self.archive[self.line] = (self.f_work, self.working)
            stale = [l for l in self.archive if l not in (self.line, self.leader_line)]
            if len(self.archive) > ARCHIVE_LINES: del self.archive[min(stale)]
        gain = 0.
        if self.f_work < self.f_best:
            gain = improvement(self.f_best, self.f_work)
            if not self.leader: self.end_excursion(gain)          # the excursion overtook: new leader
            self.best, self.f_best, self.leader_line = self.working, self.f_work, self.line
            self.curve.append((self.spent, self.f_best))
        if op != 'restart': self.policy.update(state, op, cost, local)
        if self.trace is not None:
            self.trace.append({'step': self.steps, 'spent': round(self.spent, 3), 'op': op, 'state': state,
                               'child': f, 'working': self.f_work, 'best': self.f_best,
                               'accepted': accepted, 'gain': gain, 'line': self.line, 'leader': self.leader})
        return True

    def end_excursion(self, overall):
        self.policy.excursion_done(overall, self.line_cost, self.spent)

    def resume(self):
        self.ops.append('resume')
        state = context(self.stall, self.leader)
        self.usage.setdefault(state, dict.fromkeys(self.costs, 0))['resume'] += 1
        if not self.leader:
            self.end_excursion(0.)
            self.working, self.f_work, self.line, self.stall = self.best, self.f_best, self.leader_line, self.leader_stall
        if self.trace is not None:
            self.trace.append({'step': self.steps, 'spent': round(self.spent, 3), 'op': 'resume', 'state': state,
                               'child': self.f_work, 'working': self.f_work, 'best': self.f_best,
                               'accepted': True, 'gain': 0., 'line': self.line, 'leader': self.leader})
        return True

    def run(self):
        while self.step(): pass
        return self

    def best_at(self, checkpoints):
        """Best-so-far score at each cost checkpoint (curve is a step function)."""
        out, i = [], 0
        for c in checkpoints:
            while i+1 < len(self.curve) and self.curve[i+1][0] <= c+1e-9: i += 1
            out.append(self.curve[i][1])
        return out

    def fork(self, policy, stream, window):
        """Independent continuation from this exact state for `window` more cost units."""
        clone = copy.deepcopy(self, memo={id(self.problem): self.problem, id(self.policy): policy})
        clone.rng = random.Random(f'{self.seed}/{stream}/fork')
        if hasattr(policy, 'rng'): policy.rng = random.Random(f'{self.seed}/{stream}/fork-policy')
        clone.budget, clone.trace = self.spent+window, None
        return clone
