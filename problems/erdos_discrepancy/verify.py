"""Erdős discrepancy problem, C = 2 (problem 40, Georgiev, Gómez-Serrano, Tao, Wagner 2025).

Score = length of the longest prefix x_1..x_L whose discrepancy is at most 2, plus
1 / (number of violating progressions + 1) at the first failing length, as in the official
scorer. One difference: the official scorer ignores the first list element (1-indexed);
here the candidate returns x_1, x_2, ... directly.

The official scorer recomputes every prefix from scratch; check() gives the same score
incrementally (only progressions d, 2d, ..., m with d | m change when x_m is added).
check_strict() is the official, slow formulation, used as the independent re-check.
"""
FUNCTION = "solve"
PUBLIC = [{}]
HIDDEN = []
TIMEOUT_S = 120
MAX_LEN = 5000
BEST_KNOWN = 1160      # the maximum: every +-1 sequence of length 1161 has discrepancy >= 3


def label(instance):
    return "C=2"


def best_known(instance):
    return BEST_KNOWN


def _parse(construction):
    if not isinstance(construction, list) or not construction:
        raise ValueError("expected a non-empty list of +1/-1 values")
    if len(construction) > MAX_LEN:
        raise ValueError(f"sequence longer than {MAX_LEN}")
    if any(v not in (1, -1) or isinstance(v, bool) for v in construction):
        raise ValueError("every entry must be +1 or -1")
    return [int(v) for v in construction]


def check(construction, instance):
    try:
        x = _parse(construction)
    except ValueError as e:
        return {"valid": False, "score": None, "reason": str(e)}
    L = len(x)
    divisors = [[] for _ in range(L + 1)]
    for d in range(1, L + 1):
        for m in range(d, L + 1, d):
            divisors[m].append(d)
    sums = [0] * (L + 1)               # sums[d] = x_d + x_2d + ... up to the current length
    for m in range(1, L + 1):
        violations = 0
        for d in divisors[m]:
            sums[d] += x[m - 1]
            if abs(sums[d]) > 2:
                violations += 1
        if violations:
            return {"valid": True, "score": (m - 1) + 1.0 / (violations + 1),
                    "reason": f"discrepancy exceeds 2 at length {m}"}
    return {"valid": True, "score": float(L), "reason": ""}


def check_strict(construction, instance):
    """Official formulation: test every prefix from scratch. Must agree with check()."""
    try:
        x = _parse(construction)
    except ValueError:
        return False
    for length in range(1, len(x) + 1):
        worst, count = 0, 0
        for d in range(1, length + 1):
            if length % d == 0:
                s = sum(x[i] for i in range(d - 1, length, d))
                worst = max(worst, abs(s))
                count += abs(s) > 2
        if worst > 2:
            score = (length - 1) + 1.0 / (count + 1)
            break
    else:
        score = float(len(x))
    return abs(score - check(construction, instance)["score"]) < 1e-12 and score <= BEST_KNOWN
