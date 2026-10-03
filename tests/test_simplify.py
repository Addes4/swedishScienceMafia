import unittest
from falsify.core import BEST_FIT, pack, suite
from falsify.simplify import ablate, explain, is_best_fit, normalize, simplify

class SimplifyTests(unittest.TestCase):
    def test_vestigial_terms_collapse_to_best_fit(self):
        noisy = [-3.,0,0,0,1e-4,0,0,0,0,2e-4,0,0]
        result = simplify(noisy,suite(5,100))
        self.assertTrue(is_best_fit(result['weights']))
        self.assertEqual(result['terms'],1)

    def test_normalize_preserves_packing(self):
        w = [-2.5,0,1.,0,-.3,0,0,0,0,0,-.7,0]
        for case in suite(6,30):
            self.assertEqual(pack(case['items'],w,True),pack(case['items'],normalize(w),True))

    def test_gap_term_is_load_bearing_for_best_fit(self):
        row = ablate(list(BEST_FIT),suite(7,50))[0]
        self.assertGreater(row['instances_changed'],0)
        self.assertLess(row['identical_packings'],1)

    def test_budget_is_respected(self):
        w = [-1.,.3,.2,.1,-.1,.05,-.05,.02,-.04,.01,-.14,.03]
        cases = suite(8,50)
        result = simplify(w,cases,limit=400)
        self.assertLessEqual(result['packing_executions'],400)
        self.assertTrue(result['budget_exhausted'])

    def test_explanations(self):
        self.assertIn('best-fit',explain(BEST_FIT))
        self.assertIn('first-fit',explain([0.]*12))
        self.assertIn('gap under 33',explain([-1.,0,0,0,0,0,0,0,0,0,-.14,0]))

if __name__ == '__main__': unittest.main()
