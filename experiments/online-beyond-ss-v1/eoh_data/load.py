"""Load EoH's bp_online test pickles with a restricted unpickler (only dict/list/int allowed).

The pickles come from github.com/FeiLiu36/EoH, examples/bp_online/testingdata, commit
5d3319ee3efc9190b5da8c8ed1193987e3f22519 (2026-06-28). They are regenerated here with EoH's own
generate_instances.py to check that they are byte-identical in content.
"""
import io
import pickle
from pathlib import Path

HERE = Path(__file__).resolve().parent


class _Safe(pickle.Unpickler):
    def find_class(self, module, name):
        raise pickle.UnpicklingError(f"refusing to load {module}.{name}")


def load(name):
    with open(HERE / name, "rb") as f:
        return _Safe(io.BytesIO(f.read())).load()
