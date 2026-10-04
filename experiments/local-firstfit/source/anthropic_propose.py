"""One bounded, logged API proposal. Authentication values are never logged.

This adapter does not provide an LLM memory ablation by itself. Repeated model
experiments must supply paired budgets, frozen problem definitions and fresh audits.
"""
import argparse
import json
import math
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from .core import FEATURES, write_json

def key_from_env():
    key=os.environ.get('ANTHROPIC_API_KEY')
    if not key:
        for file in [Path('.env'),Path.home()/'.env']:
            if not file.exists():continue
            for line in file.read_text().splitlines():
                if line.startswith('ANTHROPIC_API_KEY='):
                    key=line.partition('=')[2].strip().strip('\"\'')
                    if key:return key
    if not key:raise SystemExit('ANTHROPIC_API_KEY is missing. Configure it locally; never paste it into chat.')
    return key

def propose(prompt, model):
    key=key_from_env()
    if len(prompt)>12000:raise ValueError('Prompt exceeds the 12,000 character bound')
    schema={'type':'object','properties':{
        'name':{'type':'string'},'hypothesis':{'type':'string'},
        'falsification':{'type':'string'},
        'weights':{'type':'array','items':{'type':'number'},'minItems':12,'maxItems':12}},
        'required':['name','hypothesis','falsification','weights'],'additionalProperties':False}
    payload={'model':model,'max_tokens':1024,
        'system':'You propose online bin-packing scoring heuristics. Return one testable hypothesis and finite feature weights. Feasible bins only; highest score wins; first-index ties. New bins open only when no existing bin fits. No future-item access. Score is the dot product of weights with these ordered features: '+json.dumps(FEATURES),
        'messages':[{'role':'user','content':prompt}],
        'output_config':{'format':{'type':'json_schema','schema':schema}}}
    request=Request('https://api.anthropic.com/v1/messages',data=json.dumps(payload).encode(),
        headers={'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json'},method='POST')
    try:
        with urlopen(request,timeout=60) as response:result=json.load(response)
    except HTTPError as exc:
        raise SystemExit(f'Anthropic request failed with HTTP {exc.code}; response body withheld to avoid exposing credentials.') from None
    except URLError:
        raise SystemExit('Anthropic network request failed.') from None
    if result.get('stop_reason')!='end_turn':raise ValueError('Model did not complete a proposal')
    candidate=json.loads(''.join(b.get('text','') for b in result['content'] if b['type']=='text'))
    weights=candidate.get('weights',[])
    if len(weights)!=12 or not all(isinstance(w,(int,float)) and math.isfinite(w) and abs(w)<=12 for w in weights):
        raise ValueError('Candidate weights must be 12 finite values bounded by +/-12')
    return {'candidate':candidate,'prompt':prompt,'model':result['model'],'usage':result['usage'],
            'request_id':result.get('id'),'max_output_tokens':1024}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prompt-file',required=True)
    parser.add_argument('--model',default='claude-sonnet-4-6')
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    result=propose(Path(args.prompt_file).read_text(),args.model)
    write_json(args.out,result)
    print('Saved one bounded model proposal and token usage to',args.out)

if __name__=='__main__':main()
