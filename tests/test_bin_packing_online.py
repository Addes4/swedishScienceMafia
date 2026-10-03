"""Online bin-packing adapter: the gate's online protocol, the verifier and its lower bound."""
import importlib.util
import itertools
import json
import math
import random
import textwrap
from pathlib import Path

from autoresearch.gate import evaluate
from autoresearch.sandbox import run_online

ROOT = Path(__file__).resolve().parents[1]
PROBLEM = ROOT / "problems" / "bin_packing_online"


def _verify():
    spec = importlib.util.spec_from_file_location("bpo_verify", PROBLEM / "verify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _program(tmp_path, source, name="candidate.py"):
    path = tmp_path / name
    path.write_text(textwrap.dedent(source))
    return path


def _reference_best_fit(items, capacity=100):
    """Plain-list best fit, written independently of the numpy driver."""
    remaining = []
    for x in items:
        fits = [(r - x, i) for i, r in enumerate(remaining) if r >= x]
        if fits:
            remaining[min(fits)[1]] -= x
        else:
            remaining.append(capacity - x)
    return len(remaining)


def _optimal_bins(items, capacity):
    """Exact optimum by brute force over assignments (tiny instances only)."""
    n = len(items)
    for k in range(1, n + 1):
        for assignment in itertools.product(range(k), repeat=n):
            loads = [0] * k
            for b, x in zip(assignment, items):
                loads[b] += x
            if max(loads) <= capacity:
                return k
    return n


# A driver used only by these tests: it reports whether the next input was already
# readable before it decided on the current one.
_PEEK_DRIVER = r'''
import select
def drive(fn, header, next_input, emit):
    import sys
    reader = sys.modules["__main__"].reader
    while True:
        x = next_input()
        if x is None:
            return
        ready = bool(select.select([reader.fileno()], [], [], 0.05)[0])
        emit({"x": x, "decision": fn(x), "next_ready": ready})
'''


def test_online_protocol_never_reveals_the_next_input_early(tmp_path):
    prog = _program(tmp_path, "def f(x):\n    return x * 2\n")
    run = run_online(str(prog), "f", _PEEK_DRIVER, {}, [3, 1, 4, 1, 5], timeout_s=30)
    assert run.ok, run.error
    assert [d["decision"] for d in run.construction] == [6, 2, 8, 2, 10]
    assert not any(d["next_ready"] for d in run.construction)


def test_candidate_that_tries_to_pull_the_next_item_stalls_and_fails(tmp_path):
    verify = _verify()
    prog = _program(tmp_path, """
        import sys
        def priority(item, bins):
            frame = sys._getframe(1)
            peek = frame.f_locals.get("next_input") or frame.f_globals.get("next_input")
            peek()          # the parent sends nothing until this item is decided
            return -(bins - item)
    """)
    header, items = verify.online(verify.PUBLIC[0])
    run = run_online(str(prog), "priority", verify.DRIVER, header, items[:50], timeout_s=3)
    assert not run.ok and "timed out" in run.error


def test_best_fit_through_the_gate_matches_an_independent_best_fit(tmp_path):
    verify = _verify()
    metrics = evaluate(PROBLEM, str(PROBLEM / "initial.py"), str(tmp_path / "out"))
    integrity = json.loads((tmp_path / "out" / "integrity.json").read_text())
    for rec in integrity["public"] + integrity["hidden"]:
        items = verify.items_for(rec["instance"]["seed"], rec["instance"]["n"])
        assert rec["status"] == "valid"
        assert rec["score"] == verify.l2_bound(items) / _reference_best_fit(items)
    assert 0.95 < metrics["combined_score"] < 0.97


def test_invalid_priorities_are_errors_not_scores(tmp_path):
    verify = _verify()
    header, items = verify.online(verify.PUBLIC[0])
    for body in ("return -(bins - item)[:1]", "return bins * float('nan')"):
        prog = _program(tmp_path, f"def priority(item, bins):\n    {body}\n")
        run = run_online(str(prog), "priority", verify.DRIVER, header, items[:200], timeout_s=30)
        assert not run.ok


def test_check_rejects_overfull_and_malformed_assignments():
    verify = _verify()
    inst = {"name": "t", "seed": 1, "n": 200}
    items = verify.items_for(1, 200)
    assert not verify.check([0] * 200, inst)["valid"]                 # everything in one bin
    assert not verify.check(list(range(199)), inst)["valid"]          # one decision missing
    assert not verify.check(list(range(199)) + [True], inst)["valid"]
    ok = verify.check(list(range(200)), inst)                         # one item per bin
    assert ok["valid"] and ok["score"] == verify.l2_bound(items) / 200


def test_l2_bound_is_valid_and_at_least_l1():
    verify = _verify()
    rng = random.Random(5)
    for _ in range(150):
        cap = rng.choice([10, 11, 20])
        items = [rng.randint(1, cap) for _ in range(rng.randint(1, 7))]
        l2 = verify.l2_bound(items, cap)
        assert math.ceil(sum(items) / cap) <= l2 <= _optimal_bins(items, cap)
    # Large items cannot share bins: L2 sees it, L1 does not.
    assert verify.l2_bound([60] * 10) == 10 and math.ceil(600 / 100) == 6


def test_generator_matches_funsearch_weibull_parameters():
    verify = _verify()
    items = [x for seed in range(20) for x in verify.items_for(seed, 5000)]
    mean = sum(items) / len(items)
    # Weibull(scale 45, shape 3) has mean 45 * Gamma(4/3) = 40.19; truncating to integers
    # (as FunSearch's released items indicate) lowers it by about 0.5.
    assert abs(mean - (45 * math.gamma(4 / 3) - 0.5)) < 0.2
    assert min(items) >= 1 and max(items) <= 100
    assert verify.items_for(3, 100) == verify.items_for(3, 100)
    assert verify.items_for(3, 100) != verify.items_for(4, 100)
