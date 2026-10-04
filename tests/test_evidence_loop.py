import json
from pathlib import Path
import pytest

from autoresearch.live import Ledger, BudgetExceeded, LiveClient, price
from autoresearch.evidence_adapters import BoundedAdapter, CircleAdapter, RichAdapter, BEST_CODE
from autoresearch.evidence_scheduler import Scheduler
from falsify.simplify import simplify
from falsify.core import suite, pack


def test_global_budget_includes_crashed_request(tmp_path):
    p=tmp_path/'ledger.jsonl';a=Ledger(p,1.);b=Ledger(p,1.)
    first=a.reserve('first',.7,1.,{})
    with pytest.raises(BudgetExceeded):b.reserve('second',.4,1.,{})
    a.settle(first,'first',.2)
    b.reserve('second',.7,1.,{})
    assert b.totals()['committed_usd']==pytest.approx(.9)
    with pytest.raises(ValueError):a.settle(first,'first',.2)


def test_budget_tracks_incomplete_model_output(tmp_path):
    client=LiveClient(tmp_path/'run',Ledger(tmp_path/'ledger.jsonl'),1.)
    def fake(endpoint,payload):
        if endpoint.endswith('input_tokens'):return {'input_tokens':100}
        return {'id':'resp-test','model':'gpt-6.1-sol','status':'incomplete','output':[],
                'usage':{'input_tokens':100,'output_tokens':500,'input_tokens_details':{'cached_tokens':0}}}
    client.request=fake
    r=client.call('gpt-6.1-sol','test','test',max_tokens=500)
    assert r['status']=='incomplete'
    assert client.ledger.totals()['actual_usd']>0
    assert client.ledger.totals()['reserved_usd']==0


def test_network_failure_retains_reservation(tmp_path):
    client=LiveClient(tmp_path/'run',Ledger(tmp_path/'ledger.jsonl'),1.)
    def fake(endpoint,payload):
        if endpoint.endswith('input_tokens'):return {'input_tokens':100}
        raise RuntimeError('network failure')
    client.request=fake
    with pytest.raises(RuntimeError):client.call('gpt-6.1-sol','x','y')
    assert client.ledger.totals()['unresolved_requests']==1


def test_price_accounts_for_cached_input_and_reasoning():
    usage={'input_tokens':1000,'input_tokens_details':{'cached_tokens':500,'cache_write_tokens':100},
           'output_tokens':2000,'output_tokens_details':{'reasoning_tokens':1500}}
    assert price('gpt-6.1-sol',usage)==pytest.approx((400*2+500*.1+100*2.5+2000*10)/1e6)


def test_token_totals_are_scoped_to_run(tmp_path):
    ledger=Ledger(tmp_path/'ledger.jsonl')
    for name,tokens in [('first',100),('second',300)]:
        rid=ledger.reserve(name,.1,1.,{})
        ledger.settle(rid,name,.01,usage={'input_tokens':tokens,'output_tokens':tokens//2})
    assert ledger.totals('first')['input_tokens']==100
    assert ledger.totals()['output_tokens']==200


@pytest.mark.parametrize('code,expected_calls',[('rate_limit_exceeded',2),('insufficient_quota',1)])
def test_only_confirmed_rate_rejections_are_retried(tmp_path,monkeypatch,code,expected_calls):
    import io
    import autoresearch.live as live
    from urllib.error import HTTPError
    monkeypatch.setenv('OPENAI_API_KEY','unit-test-only')
    monkeypatch.setattr(live.time,'sleep',lambda seconds:None)
    calls=[]
    def fake_urlopen(request,timeout):
        calls.append(request)
        if len(calls)==1:
            body=json.dumps({'error':{'code':code,'message':'DO_NOT_LOG_SECRET'}}).encode()
            raise HTTPError(request.full_url,429,'Rejected',{},io.BytesIO(body))
        return io.BytesIO(b'{"input_tokens": 1}')
    monkeypatch.setattr(live,'urlopen',fake_urlopen)
    client=LiveClient(tmp_path/'run',Ledger(tmp_path/'ledger.jsonl'),1.)
    if code=='rate_limit_exceeded':assert client.request('responses/input_tokens',{})['input_tokens']==1
    else:
        with pytest.raises(RuntimeError,match='insufficient_quota'):client.request('responses/input_tokens',{})
    assert len(calls)==expected_calls
    assert all('DO_NOT_LOG_SECRET' not in p.read_text() for p in tmp_path.rglob('*') if p.is_file())


def test_nan_weight_rejected(tmp_path):
    a=BoundedAdapter(tmp_path)
    with pytest.raises(ValueError):a.parse(json.dumps({'weights':[float('nan')]+[0]*11}))


def test_weight_identity_ignores_integer_and_negative_zero(tmp_path):
    from autoresearch.evidence_adapters import digest
    a=BoundedAdapter(tmp_path)
    w,_=a.parse(json.dumps({'weights':[-1]+[-0.]*11}))
    assert digest(w)==digest(a.initial)


def test_score_direction_and_cache(tmp_path):
    a=BoundedAdapter(tmp_path);cases=[{'items':[63,44,32,56],'family':'witness','capacity':100}]
    best=a.evaluate(a.initial,cases,'train')
    assert best['valid'] and best['objective']==2
    a.evaluate(a.initial,cases,'again')
    assert a.executions==1


def test_explanation_cannot_hide_repair():
    # A strong half-gap reservation is known poor; deletion can repair it to best-fit.
    cases=suite(994331,120)
    original=[-1.,0,0,0,0,0,0,0,-3.,0,0,0]
    repair=simplify(original,cases,tol=0.,mode='repair')
    explained=simplify(original,cases,tol=0.,mode='explain')
    score=lambda w:sum(pack(c['items'],w) for c in cases)
    assert score(repair['weights']) < score(original)
    assert score(explained['weights']) == score(original)


def test_simplification_budget_must_cover_original():
    with pytest.raises(ValueError):simplify([-1.]+[0.]*11,suite(9,10),limit=9)


def test_rich_matches_independent_best_fit(tmp_path):
    a=RichAdapter(tmp_path);items=[63,44,32,56,28,61,9,13]
    case={'items':items,'capacity':100,'family':'test'}
    r=a.one(BEST_CODE,case)
    capacities=[]
    for x in items:
        feasible=[(g-x,i) for i,g in enumerate(capacities) if g>=x]
        if feasible:capacities[min(feasible)[1]]-=x
        else:capacities.append(100-x)
    assert r['valid'] and r['bins']==len(capacities)


def test_rich_preserves_unopened_bin_choice(tmp_path):
    a=RichAdapter(tmp_path)
    source='def priority(item,bins):\n    return bins\n'
    r=a.one(source,{'items':[20,20,20],'capacity':100,'family':'test'})
    assert r['valid'] and r['bins']==3


def test_invalid_code_scores_never_promotable(tmp_path):
    a=RichAdapter(tmp_path)
    cases=[{'items':[30,40],'capacity':100,'family':'test'}]
    r=a.evaluate('import numpy as np\ndef priority(item,bins):\n    return np.full(len(bins), np.nan)\n',cases,'train')
    assert not r['valid'] and r['objective'] is None


def test_circle_requires_strict_validity(tmp_path):
    a=CircleAdapter(tmp_path)
    invalid='def solve(n=26):\n    return [[.5,.5]]*n,[.2]*n\n'
    r=a.evaluate(invalid,a.cases(71,1),'train')
    assert not r['valid']


def test_scheduler_uses_measured_costs():
    s=Scheduler('adaptive',[1],10.,7)
    op,state,_,_=s.choose()
    s.observe(op,state,[2],9.,.123)
    estimates=s.policy.estimates(state)
    assert estimates['edit'][3]==pytest.approx(123.)
    assert s.spent==pytest.approx(123.)
