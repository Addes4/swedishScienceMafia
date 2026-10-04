"""Extract inspected public literals/functions, never execute notebook cells."""
import argparse
import ast
import hashlib
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('checkout'); args=ap.parse_args()
    source=Path(args.checkout)/'bin_packing/bin_packing.ipynb'
    notebook=json.loads(source.read_text())
    dest=Path(__file__).resolve().parents[1]/'data/funsearch'
    dest.mkdir(parents=True,exist_ok=True)
    datasets={}
    for cell in notebook['cells']:
        if cell['cell_type']!='code': continue
        text=''.join(cell['source'])
        for node in ast.parse(text).body:
            if isinstance(node,ast.Assign):
                for target in node.targets:
                    if isinstance(target,ast.Subscript) and isinstance(target.value,ast.Name) and target.value.id=='datasets':
                        datasets[ast.literal_eval(target.slice)]=ast.literal_eval(node.value)
    (dest/'datasets.json').write_text(json.dumps(datasets,sort_keys=True)+'\n')
    for index,name in [(8,'or'),(9,'weibull')]:
        text=''.join(notebook['cells'][index]['source'])
        fn=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='priority')
        (dest/f'priority_{name}.py').write_text('# Copyright 2023 DeepMind Technologies Limited. Apache-2.0.\nimport numpy as np\n\n'+ast.get_source_segment(text,fn)+'\n')
    (dest/'LICENSE').write_text((Path(args.checkout)/'LICENSE').read_text())
    metadata={'source':'https://github.com/google-deepmind/funsearch',
              'commit':'cc53f274237d7ab05c19df939edbc1f9616a7c19',
              'notebook_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'datasets':{k:len(v) for k,v in datasets.items()},
              'note':'Public evaluation data, not fresh generated audit; notebook uses L1, paper L2.',
              'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir() if p.name!='provenance.json'}}
    (dest/'provenance.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(metadata['datasets'])


if __name__=='__main__':main()
