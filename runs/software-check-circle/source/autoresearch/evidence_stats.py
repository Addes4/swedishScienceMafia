"""Paired case diagnostics; these do not estimate variation across LLM searches."""
import numpy as np


def comparison(a, b, cases, seed=71003, resamples=3000):
    if not a['valid'] or not b['valid']:
        return {'valid': False, 'reason': 'at least one required evaluation failed'}
    ds=np.array([x['objective']-y['objective'] for x,y in zip(a['rows'],b['rows'])])
    families=sorted({c['family'] for c in cases})
    rng=np.random.default_rng(seed); boots=np.zeros(resamples)
    by_family={}
    for family in families:
        sub=ds[[c['family']==family for c in cases]]
        boots += rng.choice(sub,(resamples,len(sub)),replace=True).sum(axis=1)/len(ds)
        by_family[family]={'n':len(sub),'mean_difference':float(sub.mean()),
                           'wins':int((sub<0).sum()),'ties':int((sub==0).sum()),'losses':int((sub>0).sum())}
    counts={'valid':True,'n':len(ds),'mean_difference':float(ds.mean()),
            'bootstrap_95_interval':np.quantile(boots,[.025,.975]).tolist(),
            'wins':int((ds<0).sum()),'ties':int((ds==0).sum()),'losses':int((ds>0).sum()),
            'worst_loss':float(ds.max()),'by_family':by_family,
            'uncertainty':'Stratified paired case bootstrap, conditional on this one search trajectory.'}
    if all('assignments' in x and 'assignments' in y for x,y in zip(a['rows'],b['rows'])):
        counts['identical_packings']=float(np.mean([x['assignments']==y['assignments'] for x,y in zip(a['rows'],b['rows'])]))
    return counts
