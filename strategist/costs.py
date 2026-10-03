"""Move cost tables: what one candidate of each move type costs, in budget units.

The table is a parameter of every run. Three sources:

* a name: `llm_proxy` (v1's table: one evaluation plus a generation charge that grows with the move),
  `uniform` (every move costs 1);
* a JSON file, e.g. the placeholder `experiments/strategist-v2/costs/measured_llm.json`, holding
  measured relative costs of the four moves (for an LLM loop: tokens times price per move type);
* an inline string, e.g. `edit=1,rewrite=3.1,crossover=2.4,restart=3.5`.

Measured tables are relative. By default they are rescaled so that an edit costs what it costs in the
proxy table (1.2), so the 3,000-unit budget buys about as many edits as in v1 and only the ratios
change. `resume` (going back to the leader line) evaluates nothing and is always free.
"""
import hashlib
import json
import math
from pathlib import Path
from .search import COSTS, UNIFORM_COSTS

MOVES = ('edit', 'rewrite', 'crossover', 'restart')
TABLES = {'llm_proxy': COSTS, 'uniform': UNIFORM_COSTS}
ROOT = Path(__file__).resolve().parent.parent
MEASURED = ROOT/'experiments'/'strategist-v2'/'costs'/'measured_llm.json'


class CostTableError(ValueError): pass


def normalise(relative, edit_cost=COSTS['edit']):
    missing = [m for m in MOVES if not isinstance(relative.get(m), (int, float)) or isinstance(relative.get(m), bool)]
    if missing:
        raise CostTableError(f'cost table has no numeric value for {", ".join(missing)}; '
                             'fill in the measured ratios first')
    if any(not math.isfinite(relative[m]) or relative[m] <= 0 for m in MOVES):
        raise CostTableError('every move cost must be a positive finite number')
    scale = edit_cost/relative['edit'] if edit_cost else 1.
    return {**{m: relative[m]*scale for m in MOVES}, 'resume': 0.}


def load(spec):
    """Return (name, table) for a table name, 'measured', a JSON path, or inline 'edit=1,...'."""
    if spec in TABLES: return spec, dict(TABLES[spec])
    if spec == 'measured': spec = str(MEASURED)
    if '=' in spec and not spec.endswith('.json'):
        relative = {}
        for part in spec.split(','):
            key, _, value = part.partition('=')
            relative[key.strip()] = float(value)
        return 'inline_' + '_'.join(f'{m}{relative.get(m, 0):g}' for m in MOVES), normalise(relative)
    path = Path(spec)
    if not path.exists(): raise CostTableError(f'no cost table named or found at {spec}')
    data = json.loads(path.read_text())
    edit_cost = COSTS['edit'] if data.get('normalise', True) else None
    table = normalise(data.get('relative', {}), edit_cost)
    # Each version of a measured table gets its own name (and output folder), so updated ratios never
    # overwrite or get mixed with an earlier run.
    digest = hashlib.sha256(json.dumps(table, sort_keys=True).encode()).hexdigest()[:6]
    return f"{data.get('name', path.stem)}-{digest}", table
