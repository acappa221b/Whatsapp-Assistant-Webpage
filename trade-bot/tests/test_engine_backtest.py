import tempfile
import unittest
from collections import OrderedDict
from datetime import date, timezone

from helpers import cfg, flat_then_breakout, make_session, ny, random_sessions, N
from tradebot import backtest
from tradebot.broker import BrokerError, PaperSim
from tradebot.engine import Engine
from tradebot.journal import Journal

TODAY = date(2026, 10, 19)


class FakeData:
    def __init__(self, sessions=None, fail=False):
        self.s, self.fail, self.calls = sessions, fail, 0

    def sessions(self, symbol, now=None):
        self.calls += 1
        if self.fail:
            raise OSError("rede caiu")
        return self.s


def history_plus_today(today_session, drift=0.0015):
    days = random_sessions(30, seed=3, drift=drift, vol=0.001, start=date(2026, 8, 1))
    days[TODAY] = today_session
    return days


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.j = Journal(self.tmp.name)
        self.b = PaperSim(cash=10000)

    def tearDown(self):
        self.tmp.cleanup()

    def eng(self, data, **over):
        return Engine(cfg(**over), self.b, data, self.j, "sim")

    def at(self, hh, mm):
        return ny(TODAY, hh, mm).astimezone(timezone.utc)

    def events(self):
        return [e["event"] for e in self.j.read(TODAY.isoformat())]

    def test_places_bracket_on_fresh_signal(self):
        # rompimento na barra 3 (09:45-09:50), avaliada às 09:50
        e = self.eng(FakeData(history_plus_today(flat_then_breakout(TODAY))))
        self.assertEqual(e.tick(self.at(9, 50)), "ok")
        self.assertEqual(len(self.b.orders), 1)
        o = self.b.orders[0]
        self.assertEqual((o["symbol"], o["order_class"], o["stop_loss"]["stop_price"]), ("TEST", "bracket", "100.00"))
        self.assertEqual(self.events(), ["signal", "timemachine", "order"])
        # REQ-07: não opera o mesmo ativo de novo no mesmo dia
        e.tick(self.at(9, 55))
        self.assertEqual(len(self.b.orders), 1)

    def test_req05_timemachine_blocks_without_edge(self):
        e = self.eng(FakeData(history_plus_today(flat_then_breakout(TODAY), drift=-0.0015)))
        e.tick(self.at(9, 50))
        self.assertEqual(self.b.orders, [])
        self.assertIn("timemachine", self.events())

    def test_risk_block_logged(self):
        e = self.eng(FakeData(history_plus_today(flat_then_breakout(TODAY))), max_trades_per_day=0)
        e.tick(self.at(9, 50))
        self.assertEqual(self.b.orders, [])

    def test_no_signal_no_order(self):
        e = self.eng(FakeData(history_plus_today(make_session(TODAY, [100.0] * N))))
        e.tick(self.at(10, 30))
        self.assertEqual(self.b.orders, [])

    def test_market_closed(self):
        self.b.is_open = False
        self.assertEqual(self.eng(FakeData()).tick(self.at(10, 0)), "closed")

    def test_req09_flat_by_flattens_once(self):
        e = self.eng(FakeData())
        self.assertEqual(e.tick(self.at(15, 55)), "flat")
        e.tick(self.at(15, 56))
        self.assertEqual(self.b.flattened, 1)

    def test_req09_daily_loss_halts_and_flattens(self):
        self.b.last_equity = 10200          # perdeu 200 hoje > 150
        e = self.eng(FakeData(history_plus_today(flat_then_breakout(TODAY))))
        self.assertEqual(e.tick(self.at(9, 50)), "halted")
        self.assertEqual(self.b.flattened, 1)
        self.assertEqual(self.b.orders, [])

    def test_sec05_kill_switch(self):
        self.b.pos = {"TEST": 5}
        self.j.set_kill(True)
        e = self.eng(FakeData(history_plus_today(flat_then_breakout(TODAY))))
        self.assertEqual(e.tick(self.at(9, 50)), "killed")
        self.assertEqual(self.b.flattened, 1)
        self.assertEqual(self.b.orders, [])
        self.j.set_kill(False)
        self.assertFalse(self.j.killed())

    def test_sec06_data_error_never_trades(self):
        e = self.eng(FakeData(fail=True))
        self.assertEqual(e.tick(self.at(9, 50)), "ok")
        self.assertEqual(self.b.orders, [])
        self.assertEqual(self.events(), ["error"])

    def test_sec06_broker_error_logged(self):
        def boom():
            raise BrokerError("HTTP 500")
        self.b.clock = boom
        self.assertEqual(self.eng(FakeData()).tick(self.at(10, 0)), "error")

    def test_run_forever_survives_exceptions(self):
        e = self.eng(FakeData())
        e.tick = lambda now=None: 1 / 0
        e.run_forever(sleep=lambda s: None, max_ticks=2)


class TestBacktest(unittest.TestCase):
    def test_req11_play_out(self):
        sig = {"entry": 101.0, "stop": 100.0, "target": 102.0, "slot": 3}
        up = flat_then_breakout(TODAY, after={10: 103.0})
        self.assertEqual(backtest.play_out(up, sig, 76), (1.0, "target"))
        down = flat_then_breakout(TODAY, after={10: 99.0})
        self.assertEqual(backtest.play_out(down, sig, 76), (-1.0, "stop"))

    def test_req11_walk_forward_summary(self):
        days = OrderedDict()
        for d, s in random_sessions(40, seed=11).items():
            days[d] = s
        res = backtest.run(days, cfg(), use_timemachine=False)
        self.assertGreater(res["trades"], 0)
        for k in ("win_rate", "avg_r", "total_r", "max_dd_r"):
            self.assertIn(k, res)
        filtered = backtest.run(days, cfg(), use_timemachine=True)
        self.assertLessEqual(filtered["trades"], res["trades"])

    def test_summarize_drawdown(self):
        s = backtest.summarize([{"r": 1}, {"r": -1}, {"r": -1}, {"r": 2}])
        self.assertEqual((s["total_r"], s["max_dd_r"], s["win_rate"]), (1, 2, 0.5))


if __name__ == "__main__":
    unittest.main()
