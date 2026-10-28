import unittest
from datetime import date

from helpers import cfg, ny
from tradebot import risk, sizing

D = date(2026, 10, 19)


def ctx(**over):
    c = {"now_ny": ny(D, 10, 15), "day_pnl": 0.0, "trades_today": 0, "open_positions": 0,
         "traded_symbols": [], "held_symbols": set(), "equity": 10000.0, "daytrade_count": 0,
         "mode": "paper", "killed": False, "halted": False}
    c.update(over)
    return c


ORDER = {"symbol": "TSLA", "qty": 8, "entry": 364.18, "stop": 358.32, "target": 370.04}


class TestSizing(unittest.TestCase):
    def test_req06_by_max_loss(self):
        # exemplo do README original: 50 / 5.86 -> 8 ações
        self.assertEqual(sizing.position_size(364.18, 358.32, 5000, cfg()), 8)

    def test_req06_by_max_order(self):
        self.assertEqual(sizing.position_size(100, 99.9, 100000, cfg()), 40)   # 4000/100

    def test_req06_by_cash(self):
        self.assertEqual(sizing.position_size(100, 99, 1000, cfg()), 9)        # 900/100

    def test_req06_zero(self):
        self.assertEqual(sizing.position_size(100, 101, 5000, cfg()), 0)
        self.assertEqual(sizing.position_size(500, 499, 300, cfg()), 0)


class TestRisk(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(risk.check_entry(ORDER, ctx(), cfg()), [])

    def test_req07_each_rule_blocks(self):
        cases = [
            (ctx(now_ny=ny(D, 9, 40)), "janela"),
            (ctx(now_ny=ny(D, 15, 31)), "janela"),
            (ctx(day_pnl=-150), "perda do dia"),
            (ctx(trades_today=3), "operações"),
            (ctx(open_positions=2), "posições"),
            (ctx(traded_symbols=["TSLA"]), "já operado"),
            (ctx(killed=True), "kill"),
            (ctx(halted=True), "parado"),
            (ctx(equity=20000, daytrade_count=3), "PDT"),
        ]
        for c, word in cases:
            reasons = risk.check_entry(ORDER, c, cfg())
            self.assertTrue(any(word in r for r in reasons), (word, reasons))

    def test_req07_reward_risk_and_loss(self):
        bad = dict(ORDER, target=365.0)
        self.assertTrue(risk.check_entry(bad, ctx(), cfg()))
        big = dict(ORDER, qty=20)
        self.assertTrue(any("perda no stop" in r for r in risk.check_entry(big, ctx(), cfg())))

    def test_pdt_ok_above_25k(self):
        self.assertEqual(risk.check_entry(ORDER, ctx(equity=30000, daytrade_count=5), cfg()), [])

    def test_sec04_live_limits_vs_equity(self):
        reasons = risk.check_entry(ORDER, ctx(mode="live", equity=2000), cfg())
        self.assertTrue(any("5%" in r for r in reasons))
        self.assertTrue(any("2%" in r for r in reasons))
        self.assertEqual(risk.check_entry(ORDER, ctx(mode="live", equity=10000), cfg()), [])


if __name__ == "__main__":
    unittest.main()
