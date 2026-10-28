import unittest
from datetime import date

from helpers import random_sessions
from tradebot import timemachine

SIG = {"entry": 100.0, "stop": 99.0, "target": 101.0, "slot": 3}


class TestTimeMachine(unittest.TestCase):
    def setUp(self):
        self.past = list(random_sessions(40, seed=7).values())

    def test_req04_reproducible_with_seed(self):
        pool, n = timemachine.build_pool(self.past)
        self.assertEqual(n, 40)
        a = timemachine.simulate(pool, 100, 99, 101, 3, 76, replays=300, seed=5)
        b = timemachine.simulate(pool, 100, 99, 101, 3, 76, replays=300, seed=5)
        self.assertEqual(a, b)
        self.assertAlmostEqual(a["p_target"] + a["p_stop"] + a["p_close"], 1.0)

    def test_req04_same_bar_counts_stop(self):
        # pool degenerado: toda barra vai de -2% a +2% -> stop e alvo juntos -> sempre stop
        pool = [[(1.0, 1.02, 0.98, 1.0)] for _ in range(78)]
        mc = timemachine.simulate(pool, 100, 99, 101, 3, 76, replays=50, window=0)
        self.assertEqual(mc["p_stop"], 1.0)
        self.assertEqual(mc["avg_r"], -1.0)

    def test_req04_trend_reaches_target(self):
        pool = [[(1.0, 1.003, 0.9995, 1.003)] for _ in range(78)]
        mc = timemachine.simulate(pool, 100, 99, 101, 3, 76, replays=20, window=0)
        self.assertEqual(mc["p_target"], 1.0)
        self.assertGreater(timemachine.edge(mc), 0.4)

    def test_req05_rejects_short_history(self):
        ok, rep = timemachine.evaluate(self.past[:5], SIG, 76, {"min_sessions": 20})
        self.assertFalse(ok)
        self.assertIn("insuficiente", rep["reason"])

    def test_req05_random_walk_has_no_edge(self):
        ok, rep = timemachine.evaluate(self.past, SIG, 76, {"replays": 2000, "min_edge": 0.05})
        self.assertFalse(ok)
        self.assertLess(abs(rep["edge"]), 0.1)

    def test_req05_uptrend_approved(self):
        up = list(random_sessions(30, seed=3, drift=0.0015, vol=0.001, start=date(2026, 5, 1)).values())
        ok, rep = timemachine.evaluate(up, SIG, 76, {"replays": 1000})
        self.assertTrue(ok, rep)


if __name__ == "__main__":
    unittest.main()
