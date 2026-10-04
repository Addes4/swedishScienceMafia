# EoH online bin-packing data and heuristics (third-party, MIT)

These files are copied unchanged from github.com/FeiLiu36/EoH, `examples/bp_online/`, at commit
5d3319ee3efc9190b5da8c8ed1193987e3f22519 (2026-06-28), under EoH's MIT licence (`LICENSE-EoH`).

| File | Origin |
|---|---|
| `test_dataset_{1k,2k,5k,10k,100k}.pkl`, `training_dataset_5k.pkl`, `generate_instances.py` | `testingdata/` |
| `heuristic_EoH_by_this_code.py`, `heuristic_original_EoH_paper.py`, `evaluation.py`, `runEval.py`, `results.txt` | `evaluation/` |

The pickles are read only through `load.py`, which uses a restricted unpickler that refuses any class, so
no code in them can run. They match EoH's own `generate_instances.py` exactly; this was checked when they
were downloaded (see `../RUN_LOG.md`).
