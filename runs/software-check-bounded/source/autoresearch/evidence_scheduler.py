"""Strategist bridge with actual milli-dollar costs and explicit exploratory lines."""
import math
from strategist.controller import Adaptive, Patience, context


class MeasuredAdaptive(Adaptive):
    def update(self, state, op, cost, gain):
        super().update(state, op, cost, gain)
        # Forecasts use recorded completed costs after a move has been observed.
        cells=[r[op] for r in self.cells.values() if op in r]
        pulls=sum(c[0] for c in cells)
        if pulls: self.costs[op]=max(.001,sum(c[3] for c in cells)/pulls)


class Scheduler:
    def __init__(self, policy, initial, score, seed):
        self.kind=policy
        self.costs={'edit':30.,'rewrite':50.,'crossover':60.,'restart':50.,'resume':0.}
        self.policy=MeasuredAdaptive(self.costs,seed,memory=1000.,prior_cost=100.) if policy=='adaptive' else Patience(4)
        self.working=self.best=initial
        self.f_work=self.f_best=self.f_start=score
        self.line=self.leader_line=0
        self.stall=self.leader_stall=self.steps=0
        self.spent=self.line_cost=0.
        self.archive={0:(score,initial)}
        self.warmup=['edit','rewrite','restart','crossover'] if policy=='adaptive' else []

    @property
    def leader(self): return self.line==self.leader_line

    def progress_rate(self):
        return max(0,self.f_start-self.f_best)/max(abs(self.f_start),1.)/max(self.spent,.001)

    def choose(self):
        state=context(self.stall,self.leader)
        reason={'state':state,'policy':self.kind,'cost_unit':'measured milli-USD; initial forecasts only'}
        if self.warmup:
            op=self.warmup.pop(0);reason['warmup']=True
        else:
            op=self.policy.choose(state,self)
            if self.kind=='adaptive':reason.update(self.policy.explain(state,self))
        if op=='resume':
            self.policy.excursion_done(0.,self.line_cost,self.spent)
            self.working,self.f_work=self.best,self.f_best
            self.line,self.stall=self.leader_line,self.leader_stall
            self.line_cost=0.
            state=context(self.stall,True);op='edit';reason['resumed_leader']=True
        partner=next((x for f,x in sorted(self.archive.values(),key=lambda z:z[0]) if x!=self.working),self.best)
        if op=='restart':
            if self.leader:self.leader_stall=self.stall
            else:self.policy.excursion_done(0.,self.line_cost,self.spent)
            self.line+=1;self.line_cost=0.;self.stall=0
        return op,state,partner,reason

    def observe(self, op, state, child, score, usd):
        cost=max(.001,usd*1000.)
        self.spent+=cost;self.line_cost+=cost;self.steps+=1
        old=self.f_work
        improved=score is not None and score<old-1e-12
        if score is not None and (op=='restart' or score<=self.f_work):
            self.working,self.f_work=child,score
        self.stall=0 if improved else self.stall+1
        gain=max(0,old-score)/max(abs(old),1.) if score is not None else 0.
        if self.f_work<self.archive.get(self.line,(math.inf,None))[0]:
            self.archive[self.line]=(self.f_work,self.working)
        if self.f_work<self.f_best:
            if not self.leader:self.policy.excursion_done((self.f_best-self.f_work)/max(abs(self.f_best),1.),self.line_cost,self.spent)
            self.best,self.f_best,self.leader_line=self.working,self.f_work,self.line
        if op!='restart':self.policy.update(state,op,cost,gain)
        elif self.kind=='adaptive': self.costs['restart']=cost
