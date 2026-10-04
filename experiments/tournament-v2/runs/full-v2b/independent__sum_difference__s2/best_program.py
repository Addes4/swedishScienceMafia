import math, random, time

def solve():
    random.seed(12345)
    deadline = time.time() + 115.0

    def score(A):
        A = list(set(A))
        if len(A) < 2:
            return -1.0, 0, 0
        diffs = set()
        sums = set()
        n = len(A)
        for i in range(n):
            ai = A[i]
            for j in range(n):
                diffs.add(ai - A[j])
                sums.add(ai + A[j])
        d = len(diffs)
        s = len(sums)
        if s <= 1:
            return -1.0, d, s
        val = math.log(d) / math.log(s) + (1.0 - 1.0 / n) / 100.0
        return val, d, s

    # Start from a strong known family: B_2 / Golomb-style sparse set plus a dense interval.
    # Small Golomb ruler (optimal 8-mark ruler) gives large difference set.
    ruler = [0, 1, 4, 9, 15, 22, 32, 34]
    A = ruler[:]
    # Add a dense block offset far away to increase |A| and differences while controlling sums.
    base = 1000
    block_len = 80
    dense = [base + 3*i for i in range(block_len)]
    A.extend(dense)

    best = A[:]
    best_val, best_d, best_s = score(best)

    # Local search: mutate elements, occasionally add/remove, accept improvements and sometimes sideways moves.
    cur = best[:]
    cur_val = best_val
    it = 0
    while time.time() < deadline:
        it += 1
        cand = cur[:]
        if random.random() < 0.15 and len(cand) < 4000:
            # add a point from a range around existing structure
            if random.random() < 0.5:
                x = random.choice(cand)
                y = random.choice(cand)
                cand.append((x + y) // 2 + random.randint(-5, 5))
            else:
                cand.append(random.randint(-2000, 2000))
        elif random.random() < 0.05 and len(cand) > 3:
            del cand[random.randrange(len(cand))]
        else:
            i = random.randrange(len(cand))
            step = random.choice([1,2,3,5,8,13,21,34,55])
            cand[i] += random.randint(-step, step)

        cand = list(set(cand))
        if len(cand) < 2:
            continue
        val, d, s = score(cand)
        if val > cur_val or (val == cur_val and random.random() < 0.01):
            cur, cur_val = cand[:], val
            if val > best_val or (val == best_val and len(cand) > len(best)):
                best, best_val, best_d, best_s = cand[:], val, d, s
        else:
            # occasionally restart from best to escape local optima
            if random.random() < 0.002:
                cur = best[:]
                cur_val = best_val

    # Final greedy polish using full score on candidate moves.
    improved = True
    while improved and time.time() < deadline:
        improved = False
        order = list(range(len(best)))
        random.shuffle(order)
        for i in order:
            old = best[i]
            for delta in [1,-1,2,-2,3,-3,5,-5,8,-8,13,-13,21,-21,34,-34]:
                cand = best[:]
                cand[i] = old + delta
                cand = list(set(cand))
                if len(cand) < 2:
                    continue
                val, d, s = score(cand)
                if val > best_val + 1e-12:
                    best, best_val, best_d, best_s = cand, val, d, s
                    improved = True
                    break
            if improved:
                break

    return sorted(set(best))
