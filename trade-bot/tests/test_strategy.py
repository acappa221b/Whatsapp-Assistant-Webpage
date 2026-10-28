import unittest
from datetime import date

from helpers import N, cfg, flat_then_breakout, make_session
from tradebot import strategy

D = date(2026, 10, 19)


class TestORB(unittest.TestCase):
    def test_req01_opening_range(self):
        s = flat_then_breakout(D)
        self.assertEqual(strategy.opening_range(s, 3), (100.2, 99.8))

    def test_req02_waiting_before_range_closes(self):
        s = flat_then_breakout(D)
        self.assertEqual(strategy.orb_signal(s, 2, cfg())["status"], "waiting")

    def test_req02_triggered_on_fresh_close(self):
        sig = strategy.orb_signal(flat_then_breakout(D), 3, cfg())
        self.assertEqual(sig["status"], "triggered")
        self.assertEqual(sig["entry"], 101.0)
        self.assertEqual(sig["slot"], 3)

    def test_req02_expired_when_not_latest(self):
        self.assertEqual(strategy.orb_signal(flat_then_breakout(D), 5, cfg())["status"], "expired")

    def test_none_without_breakout(self):
        s = make_session(D, [100.0] * N)
        self.assertEqual(strategy.orb_signal(s, 10, cfg())["status"], "none")

    def test_req03_stop_mid_and_target_1r(self):
        sig = strategy.orb_signal(flat_then_breakout(D), 3, cfg())
        self.assertEqual(sig["stop"], 100.0)
        self.assertEqual(sig["risk"], 1.0)
        self.assertEqual(sig["target"], 102.0)

    def test_req03_stop_or_low_and_2r(self):
        sig = strategy.orb_signal(flat_then_breakout(D), 3, cfg(stop_rule="or_low", target_r=2.0))
        self.assertEqual(sig["stop"], 99.79)
        self.assertAlmostEqual(sig["target"], 101.0 + 2 * 1.21, places=2)

    def test_invalid_when_range_missing(self):
        s = flat_then_breakout(D)
        s[1] = None
        self.assertEqual(strategy.orb_signal(s, 3, cfg())["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
