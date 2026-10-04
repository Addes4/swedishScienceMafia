# Baseline for the Thomson problem: basin hopping (Wales and Doye 1997), the standard method for this landscape.
# Random starts, then perturb a parent (10% fresh random starts) and let the framework relax it. Uses no context.
def initialize(record, neighbours, rng, count):
    return [(rng.normal(size=(n, 3)), 0.0) for _ in range(count)]


def vary(parents, rng, count):
    out, spacing = [], math.sqrt(4*math.pi/n)
    for _ in range(count):
        if rng.random() < 0.1:
            out.append((rng.normal(size=(n, 3)), 0.0))
            continue
        points = parents[int(min(rng.integers(len(parents), size=2)))][0]
        out.append((points+rng.normal(scale=0.25*spacing, size=points.shape), 0.0))
    return out
