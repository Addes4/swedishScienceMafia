import io
import json
import threading
import time
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

import pytest

from autoresearch.evidence_adapters import RichAdapter, case_id
from autoresearch.live import Ledger
from autoresearch.throughput import HeaderClient, RateCoordinator, duration, retry_after


@pytest.mark.parametrize('value,expected', [('1m2.5s',62.5),('500ms',.5),('2h',7200),('bad',None)])
def test_header_durations(value,expected):
    assert duration(value)==expected


def test_retry_after_http_date():
    assert retry_after({'retry-after':'Thu, 01 Jan 1970 00:16:47 GMT'},1000)==7


def fake_clock(monkeypatch):
    import autoresearch.throughput as transport
    clock=[1000.]
    monkeypatch.setattr(transport,'time',SimpleNamespace(time=lambda:clock[0],monotonic=lambda:clock[0],
                        sleep=lambda seconds:clock.__setitem__(0,clock[0]+seconds)))
    return clock


def test_headers_coordinate_separate_clients_without_blanket_delay(tmp_path,monkeypatch):
    clock=fake_clock(monkeypatch)
    a=RateCoordinator(tmp_path/'usage.jsonl');b=RateCoordinator(tmp_path/'usage.jsonl')
    ticket,wait=a.acquire('test',10,30)
    assert wait==0
    a.release(ticket,'test',{'x-ratelimit-remaining-tokens':'5','x-ratelimit-reset-tokens':'2s'})
    ticket,wait=b.acquire('test',10,30)
    assert wait==2
    b.release(ticket,'test',{})
    ticket,wait=a.acquire('test',10,30)
    assert wait==0


def test_max_concurrency_and_expired_lease_recovery(tmp_path,monkeypatch):
    clock=fake_clock(monkeypatch)
    r=RateCoordinator(tmp_path/'usage.jsonl')
    r.acquire('a',10,1);r.acquire('b',10,1)
    _,wait=r.acquire('c',10,1)
    assert wait>=31


@pytest.mark.parametrize('code,status,retries', [('rate_limit_exceeded',429,True),
                          ('server_is_overloaded',503,True),('insufficient_quota',429,False)])
def test_transport_honors_retry_after_and_redacts_errors(tmp_path,monkeypatch,code,status,retries):
    import autoresearch.throughput as transport
    clock=fake_clock(monkeypatch)
    monkeypatch.setenv('OPENAI_API_KEY','unit-test-key')
    calls=[]
    def send(request,timeout):
        calls.append(clock[0])
        if len(calls)==1:
            body=json.dumps({'error':{'code':code,'message':'SECRET_MUST_NOT_APPEAR'}}).encode()
            raise HTTPError(request.full_url,status,'Rejected',{'retry-after':'7'},io.BytesIO(body))
        response=io.BytesIO(b'{"input_tokens": 2}')
        response.headers={};response.status=200
        return response
    monkeypatch.setattr(transport,'urlopen',send)
    c=HeaderClient(tmp_path/'run',Ledger(tmp_path/'usage.jsonl'),1.)
    if retries:
        assert c.request('responses/input_tokens',{'model':'test'})['input_tokens']==2
        assert calls[1]-calls[0]>=7
    else:
        with pytest.raises(RuntimeError,match=code):c.request('responses/input_tokens',{'model':'test'})
        assert len(calls)==1
    assert 'SECRET_MUST_NOT_APPEAR' not in (tmp_path/'run/transport.jsonl').read_text()


def test_large_retry_after_defers_instead_of_retrying_early(tmp_path,monkeypatch):
    import autoresearch.throughput as transport
    fake_clock(monkeypatch);monkeypatch.setenv('OPENAI_API_KEY','unit-test-key')
    calls=[]
    def send(request,timeout):
        calls.append(1)
        raise HTTPError(request.full_url,429,'Rejected',{'retry-after':'600'},
                        io.BytesIO(b'{"error":{"code":"rate_limit_exceeded"}}'))
    monkeypatch.setattr(transport,'urlopen',send)
    c=HeaderClient(tmp_path/'run',Ledger(tmp_path/'usage.jsonl'),1.)
    with pytest.raises(RuntimeError):c.request('responses/input_tokens',{'model':'test'})
    assert len(calls)==1


def test_network_failure_not_retried_and_lease_released(tmp_path,monkeypatch):
    import autoresearch.throughput as transport
    monkeypatch.setenv('OPENAI_API_KEY','unit-test-key');calls=[]
    def send(request,timeout):
        calls.append(1);raise URLError('private error')
    monkeypatch.setattr(transport,'urlopen',send)
    c=HeaderClient(tmp_path/'run',Ledger(tmp_path/'usage.jsonl'),1.)
    with pytest.raises(RuntimeError,match='network request failed'):
        c.request('responses/input_tokens',{'model':'test'})
    assert len(calls)==1
    assert json.loads(c.rates.path.read_text())['leases']=={}


def test_parallel_cases_keep_order_deduplicate_and_reject_any_invalid(tmp_path):
    adapter=RichAdapter(tmp_path,workers=3)
    cases=[{'family':'test','seed':i,'items':[10]} for i in range(4)]
    calls=[];lock=threading.Lock();active=0;peak=0
    def one(payload,case):
        nonlocal active,peak
        with lock:
            calls.append(case['seed']);active+=1;peak=max(peak,active)
        time.sleep(.02*(4-case['seed']))
        with lock:active-=1
        return {'valid':case['seed']!=2,'objective':case['seed']}
    adapter.one=one
    result=adapter.evaluate('fixture',cases+[cases[0]],'first')
    assert not result['valid'] and result['objective'] is None
    assert [r['case_id'] for r in result['rows']]==[case_id(c) for c in cases+[cases[0]]]
    assert len(calls)==4 and 1<peak<=3
    assert adapter.metrics()['physical_executions']==4
    adapter.evaluate('fixture',cases,'cached')
    assert len(calls)==4
