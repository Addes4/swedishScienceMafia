import random
import unittest
from falsify.core import BEST_FIT, mutate, pack, suite

def reference(items,weights=BEST_FIT):
    bins=[]
    for item in items:
        feasible=[i for i,r in enumerate(bins) if r>=item]
        if feasible:
            chosen=min(feasible,key=lambda i:bins[i])
            bins[chosen]-=item
        else: bins.append(100-item)
    return len(bins)

class PackingTests(unittest.TestCase):
    def test_best_fit_matches_independent_implementation(self):
        for case in suite(42,100):
            self.assertEqual(pack(case['items']),reference(case['items']))

    def test_mutated_candidates_produce_valid_packings(self):
        rng=random.Random(1)
        for case in suite(79,100):
            weights=mutate(BEST_FIT,rng)
            bins,assignments=pack(case['items'],weights,True)
            loads=[0]*bins
            for item,b in zip(case['items'],assignments): loads[b]+=item
            self.assertTrue(all(0<load<=100 for load in loads))
            self.assertEqual(sum(loads),sum(case['items']))

    def test_reject_invalid_input(self):
        for items in [[0],[101],[-1],[1.5],[True]]:
            with self.assertRaises(ValueError): pack(items)

    def test_reject_nonfinite_weights_even_for_one_item(self):
        with self.assertRaises(ValueError): pack([20],[float('nan')]*12)

    def test_small_counterexample_and_revision(self):
        items=[63,44,32,56]
        bad=[-.2,0,.05,1,-.1,0,0,-1.5,0,0,0,0]
        repaired=[.25,0,3,1,-.02,0,0,0,0,0,0,0]
        self.assertEqual(pack(items,bad),3)
        self.assertEqual(pack(items,repaired),2)

if __name__=='__main__': unittest.main()
