"""Discover -> simplify -> explain: shrink a winning heuristic to a short rule and test which terms matter."""
import argparse
import json
import math
import random
import statistics
from pathlib import Path
from .core import BEST_FIT, FEATURES, TRAIN_FAMILIES, SHIFT_FAMILIES, pack, suite, write_json

INDICATORS = {3:'an exact fit', 4:'a sliver gap under 10', 5:'a gap smaller than the current item',
              6:'a gap that could hold another copy of the item', 10:'a non-zero gap under 33',
              11:'a non-zero gap under 50'}
CENTRES = {7:25, 8:50, 9:75}

class Budget:
    def __init__(self, limit): self.limit, self.used = limit, 0
    def charge(self, n):
        if self.used+n > self.limit: return False
        self.used += n; return True

def bins(weights, cases):
    return [pack(x['items'],weights) for x in cases]

def traces(weights, cases):
    return [pack(x['items'],weights,True)[1] for x in cases]

def terms(weights):
    return [j for j,w in enumerate(weights) if w != 0]

def normalize(weights):
    scale = max(abs(w) for w in weights)
    return [w/scale if scale else 0. for w in weights]

def bootstrap(diffs, seed=739, n=10000):
    rng = random.Random(seed)
    boot = sorted(statistics.mean(rng.choices(diffs,k=len(diffs))) for _ in range(n))
    return [boot[int(.025*n)], boot[int(.975*n)-1]]

def agreement(a, b):
    same = sum(x==y for s,t in zip(a,b) for x,y in zip(s,t))
    return {'identical_packings':statistics.mean(s==t for s,t in zip(a,b)),
            'placement_agreement':same/sum(len(s) for s in a)}

def nice_values(x):
    """Nearest {1,2,5} x 10^k values to x, closest first."""
    if x == 0: return []
    vs = {math.copysign(m*10.**e,x) for m in (1,2,5) for e in range(-3,2)}
    return sorted(vs,key=lambda v:abs(math.log(abs(v/x))))[:3]

def simplify(weights, cases, tol=.002, limit=150000, mode='repair'):
    """Greedy term elimination then weight rounding, accepted while mean bins stay within tol of the original."""
    if mode not in ('repair', 'explain'):
        raise ValueError('mode must be repair or explain')
    if not cases or limit < len(cases) or tol < 0:
        raise ValueError('Need cases, nonnegative tolerance, and budget for the original')
    budget = Budget(limit)
    current = normalize(weights)
    budget.charge(len(cases))
    target = statistics.mean(bins(current,cases))+tol
    original_score = target-tol
    def acceptable(s):
        return s <= target if mode == 'repair' else abs(s-original_score) <= tol+1e-12
    steps = [{'step':'start','weights':current,'mean_bins':target-tol}]
    def score(w):
        return statistics.mean(bins(w,cases)) if budget.charge(len(cases)) else None
    # Greedy elimination can stall in a basin, so first ask whether one existing term already suffices.
    singles = []
    for j in terms(current) if len(terms(current)) > 1 else []:
        w = [0.]*12; w[j] = math.copysign(1.,current[j])
        s = score(w)
        if s is not None and acceptable(s): singles.append((s,-abs(current[j]),j,w))
    if singles:
        s,_,j,current = min(singles,key=lambda t:t[:3])
        steps.append({'step':f'keep only {FEATURES[j]}','weights':current,'mean_bins':s})
    while len(terms(current)) > 1:
        trials = []
        for j in terms(current):
            w = list(current); w[j] = 0.
            s = score(w)
            if s is None: break
            trials.append((s,abs(current[j]),j,w))
        trials = [t for t in trials if acceptable(t[0])]
        if not trials: break
        # Ties go to dropping the smallest term, so equal-quality but less readable rules are not kept.
        s,_,j,w = min(trials,key=lambda t:t[:3])
        current = normalize(w)
        steps.append({'step':f'drop {FEATURES[j]}','weights':current,'mean_bins':s})
    for j in sorted(terms(current),key=lambda j:-abs(current[j])):
        for v in nice_values(current[j]):
            if v == current[j]: break
            w = list(current); w[j] = v
            s = score(w)
            if s is None: break
            if acceptable(s):
                current = w
                steps.append({'step':f'round {FEATURES[j]} -> {v:g}','weights':current,'mean_bins':s})
                break
    return {'weights':current,'terms':len(terms(current)),'original_terms':len(terms(weights)),
            'steps':steps,'packing_executions':budget.used,'budget_exhausted':budget.used+len(cases)>limit,
            'tolerance':tol, 'mode':mode}

# Single terms that are strictly monotone in gap >= 0 make exactly the best-fit (-1) or worst-fit (+1) choice.
MONOTONE = {0:1, 1:1, 2:-1}

def fit_direction(weights):
    js = terms(weights)
    if len(js) != 1 or js[0] not in MONOTONE: return 0
    return int(math.copysign(1,weights[js[0]]))*MONOTONE[js[0]]

def is_best_fit(weights):
    return fit_direction(weights) == -1

def formula(weights):
    return ' '.join(f'{w:+g}*[{FEATURES[j]}]' for j,w in enumerate(weights) if w) or '0'

def explain(weights):
    """Plain-language reading of a scoring rule; the highest score wins and ties go to the earliest bin."""
    w = normalize(weights)
    if not terms(w): return 'Every bin scores the same, so the first feasible bin wins: this is first-fit.'
    if is_best_fit(w): return f'Put each item in the feasible bin that leaves the smallest gap: [{formula(w)}] is exactly best-fit.'
    if fit_direction(w) == 1: return f'Put each item in the feasible bin that leaves the largest gap: [{formula(w)}] is exactly worst-fit.'
    parts = []
    lead = w[0]
    if lead < 0: parts.append('prefer the bin that leaves the smallest gap (best-fit)')
    elif lead > 0: parts.append('prefer the bin that leaves the largest gap (worst-fit)')
    for j in terms(w):
        if j == 0: continue
        if j in INDICATORS:
            verb = 'reward' if w[j] > 0 else 'penalise'
            size = f' worth about {100*abs(w[j]/lead):.3g} units of capacity' if lead else f' with weight {abs(w[j]):g}'
            parts.append(f'{verb} leaving {INDICATORS[j]}{size}')
        elif j in CENTRES:
            c = CENTRES[j]
            side = (f'best-fit below {c}, worst-fit above' if w[j] > 0 else f'worst-fit below {c}, best-fit above')
            parts.append(f"prefer leftover gaps {'far from' if w[j] > 0 else 'close to'} {c} "
                         f"({side}) with weight {abs(w[j]):g}")
        else:
            parts.append(f'add a {w[j]:+g} x {FEATURES[j]} shaping term')
    text = ', '.join(parts[:1]+[('but ' if i==0 else 'and ')+p for i,p in enumerate(parts[1:])])
    return text[0].upper()+text[1:]+'.'

def compare(a, b, cases, a_bins=None, b_bins=None):
    """Paired comparison of rule a against rule b; negative mean difference favours a."""
    xa = a_bins or bins(a,cases); xb = b_bins or bins(b,cases)
    ds = [p-q for p,q in zip(xa,xb)]
    return {'mean_bins_a':statistics.mean(xa),'mean_bins_b':statistics.mean(xb),
            'mean_difference':statistics.mean(ds),'bootstrap_95_interval':bootstrap(ds),
            'wins':sum(d<0 for d in ds),'ties':sum(d==0 for d in ds),'losses':sum(d>0 for d in ds),
            **agreement(traces(a,cases),traces(b,cases))}

def ablate(weights, cases):
    """Zero one term at a time; positive bin change means the term was helping."""
    base = bins(weights,cases)
    base_traces = traces(weights,cases)
    out = []
    for j in terms(weights):
        w = list(weights); w[j] = 0.
        xs = bins(w,cases)
        ds = [a-b for a,b in zip(xs,base)]
        out.append({'feature':FEATURES[j],'weight':weights[j],'mean_bin_change':statistics.mean(ds),
                    'bootstrap_95_interval':bootstrap(ds),'instances_changed':sum(d!=0 for d in ds),
                    **agreement(traces(w,cases),base_traces)})
    return out

def shrink(items, keep, budget=2000):
    """Greedy deletion while keep(items) holds; a small witness, not a proof of minimality."""
    current, used, changed = list(items), 0, True
    while changed and used < budget:
        changed = False
        for i in range(len(current)):
            trial = current[:i]+current[i+1:]
            used += 1
            if trial and keep(trial): current, changed = trial, True; break
    return current

def witness(weights, cases):
    """Smallest found instance where the rule and best-fit use a different number of bins (wins preferred)."""
    gaps = [(pack(x['items'],weights)-pack(x['items']),i) for i,x in enumerate(cases)]
    differing = sorted((g,i) for g,i in gaps if g)
    if not differing: return None
    gap,i = differing[0]
    keep = (lambda xs:pack(xs,weights)<pack(xs)) if gap < 0 else (lambda xs:pack(xs,weights)>pack(xs))
    items = shrink(cases[i]['items'],keep)
    cb,ct = pack(items,weights,True); rb,rt = pack(items,BEST_FIT,True)
    return {'kind':'rule beats best-fit' if gap<0 else 'best-fit beats rule','family':cases[i]['family'],
            'items':items,'rule_bins':cb,'best_fit_bins':rb,'rule_assignments':ct,'best_fit_assignments':rt}

def load_candidates(paths):
    out, seen = [], set()
    for path in paths:
        data = json.loads(Path(path).read_text())
        rows = data['candidates'] if isinstance(data,dict) else data
        for r in rows:
            name = r.get('name') or f"{r['arm']}-{r['seed']}"
            key = tuple(round(w,9) for w in normalize(r['weights']))
            if key in seen: continue
            seen.add(key); out.append({'name':name,'source':str(path),'weights':[float(w) for w in r['weights']]})
    return out

def markdown(report):
    w, s, c = report['winner'], report['simplified'], report['confirmation']
    lines = [f"# Discover, simplify, explain\n",
             f"Winner on the selection suite: **{w['name']}** ({w['source']}), {w['terms']} non-zero terms.\n",
             f"Original: `{formula(w['normalized'])}`\n",
             f"Simplified ({s['original_terms']} -> {s['terms']} terms, {s['packing_executions']} packing executions): `{formula(s['weights'])}`\n",
             f"**Rule:** {report['explanation']}\n",
             "## Simplification trace (simplification suite)\n", "| step | mean bins |", "|---|---|"]
    lines += [f"| {x['step']} | {x['mean_bins']:.4f} |" for x in s['steps']]
    lines += ["\n## Confirmation suite (fresh, includes shifted families)\n",
              "| comparison | mean A | mean B | A-B | 95% CI | W/T/L | identical packings | placement agreement |",
              "|---|---|---|---|---|---|---|---|"]
    for name,r in c.items():
        lo,hi = r['bootstrap_95_interval']
        lines.append(f"| {name} | {r['mean_bins_a']:.4f} | {r['mean_bins_b']:.4f} | {r['mean_difference']:+.4f} | "
                     f"[{lo:+.4f}, {hi:+.4f}] | {r['wins']}/{r['ties']}/{r['losses']} | "
                     f"{r['identical_packings']:.3f} | {r['placement_agreement']:.4f} |")
    for title,key in [('Ablations of the simplified rule (confirmation suite)','ablation_simplified'),
                      ('Ablations of the original winner (confirmation suite)','ablation_original')]:
        lines += [f"\n## {title}\n", "| removed term | weight | mean bin change | 95% CI | instances changed | identical packings |",
                  "|---|---|---|---|---|---|"]
        for a in report[key]:
            lo,hi = a['bootstrap_95_interval']
            lines.append(f"| {a['feature']} | {a['weight']:+.3g} | {a['mean_bin_change']:+.4f} | [{lo:+.4f}, {hi:+.4f}] | "
                         f"{a['instances_changed']} | {a['identical_packings']:.3f} |")
    wt = report['witness']
    lines.append("\n## Witness\n")
    if wt: lines.append(f"{wt['kind']} on a shrunken {wt['family']} instance of {len(wt['items'])} items "
                        f"({wt['rule_bins']} vs {wt['best_fit_bins']} bins): `{wt['items']}`\n")
    else: lines.append("No confirmation instance where the simplified rule and best-fit differ in bin count.\n")
    m = report['map']
    lines += ["## Simplification map (all distinct candidates)\n",
              f"{m['candidates']} candidates, mean {m['mean_terms_before']:.2f} -> {m['mean_terms_after']:.2f} terms; "
              f"{m['reduce_to_best_fit']} reduce to exactly best-fit, {m['reduce_to_first_fit']} to first-fit.\n",
              "| surviving term | candidates |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k,v in m['surviving_terms'].items()]
    return '\n'.join(lines)+'\n'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidates',nargs='+',default=['experiments/local-v1/audit.json',
        'experiments/codex_candidates.json','experiments/codex_revision.json'])
    parser.add_argument('--weights',type=float,nargs=12,help='simplify this vector instead of selecting a winner')
    parser.add_argument('--tol',type=float,default=.002)
    parser.add_argument('--budget',type=int,default=150000)
    parser.add_argument('--out',default='experiments/simplify-v1')
    args = parser.parse_args()
    selection = suite(7000001,500)
    simplification = suite(7000002,1000)
    candidates = ([{'name':'manual','source':'--weights','weights':args.weights}] if args.weights
                  else load_candidates(args.candidates))
    for c in candidates: c['selection_mean_bins'] = statistics.mean(bins(c['weights'],selection))
    winner = min(candidates,key=lambda c:(c['selection_mean_bins'],-len(terms(c['weights']))))
    print('winner',winner['name'],winner['selection_mean_bins'],flush=True)
    simple = simplify(winner['weights'],simplification,args.tol,args.budget)
    print('simplified',formula(simple['weights']),flush=True)
    # Confirmation data is generated only after simplification has finished.
    confirmation = suite(7000003,800,TRAIN_FAMILIES+SHIFT_FAMILIES)
    original = normalize(winner['weights'])
    ob, sb, rb = bins(original,confirmation), bins(simple['weights'],confirmation), bins(BEST_FIT,confirmation)
    report = {'protocol':'experiments/SIMPLIFY_PROTOCOL.md',
        'winner':{**winner,'normalized':original,'terms':len(terms(original))},
        'simplified':simple,'explanation':explain(simple['weights']),
        'confirmation':{'simplified vs original':compare(simple['weights'],original,confirmation,sb,ob),
                        'simplified vs best-fit':compare(simple['weights'],BEST_FIT,confirmation,sb,rb),
                        'original vs best-fit':compare(original,BEST_FIT,confirmation,ob,rb)},
        'by_family':{f:{'original':statistics.mean(o-r for x,o,r in zip(confirmation,ob,rb) if x['family']==f),
                        'simplified':statistics.mean(s-r for x,s,r in zip(confirmation,sb,rb) if x['family']==f)}
                     for f in TRAIN_FAMILIES+SHIFT_FAMILIES},
        'ablation_simplified':ablate(simple['weights'],confirmation),
        'ablation_original':ablate(original,confirmation),
        'witness':witness(simple['weights'],confirmation)}
    rows = []
    for c in candidates:
        r = simplify(c['weights'],simplification,args.tol,args.budget)
        rows.append({'name':c['name'],'terms_before':r['original_terms'],'terms_after':r['terms'],'weights':r['weights'],
                     'rule':explain(r['weights']),'packing_executions':r['packing_executions']})
    survivors = {}
    for r in rows:
        for j in terms(r['weights']): survivors[FEATURES[j]] = survivors.get(FEATURES[j],0)+1
    report['map'] = {'candidates':len(rows),'mean_terms_before':statistics.mean(r['terms_before'] for r in rows),
        'mean_terms_after':statistics.mean(r['terms_after'] for r in rows),
        'reduce_to_best_fit':sum(is_best_fit(r['weights']) for r in rows),
        'reduce_to_first_fit':sum(not terms(r['weights']) for r in rows),
        'surviving_terms':dict(sorted(survivors.items(),key=lambda kv:-kv[1])),'rows':rows}
    out = Path(args.out)
    write_json(out/'report.json',report)
    (out/'report.md').write_text(markdown(report))
    print(markdown(report),flush=True)

if __name__ == '__main__': main()
