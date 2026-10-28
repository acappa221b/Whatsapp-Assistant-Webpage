"""Demonstração offline: o robô de verdade operando um pregão SINTÉTICO.

Três ativos fictícios (ACME, BRVO, CIRC) com 30 pregões de histórico cada:
  ACME rompe a faixa e tem histórico favorável  -> Máquina do Tempo aprova -> ordem -> alvo
  BRVO rompe a faixa mas o histórico é fraco    -> Máquina do Tempo veta
  CIRC não rompe a faixa                        -> nada acontece

Uso: python3 demo/replay.py [--json saida.json]
"""

import json
import os
import random
import sys
import tempfile
from collections import OrderedDict
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tradebot import clock  # noqa: E402
from tradebot.broker import PaperSim  # noqa: E402
from tradebot.engine import Engine  # noqa: E402
from tradebot.journal import Journal  # noqa: E402

BM, N = 5, clock.session_slots(5)
TODAY = date(2026, 10, 27)


def ts(d, slot):
    return int((datetime(d.year, d.month, d.day, 9, 30, tzinfo=clock.NY) + timedelta(minutes=BM * slot)).timestamp())


def session(d, closes, spread):
    out, prev = [], closes[0]
    for i, c in enumerate(closes):
        out.append({"t": ts(d, i), "o": prev, "h": max(prev, c) + spread, "l": min(prev, c) - spread, "c": c, "v": 1000})
        prev = c
    return out


def history(seed, drift, vol, base):
    rng, days, d = random.Random(seed), OrderedDict(), TODAY - timedelta(days=45)
    while d < TODAY:
        if d.weekday() < 5:
            p, closes = base, []
            for _ in range(N):
                p *= 1 + rng.gauss(drift, vol)
                closes.append(round(p, 2))
            days[d] = session(d, closes, spread=base * 0.0004)
        d += timedelta(days=1)
    return days


def today_path(base, breakout_at, drift, seed):
    """Faixa de ~1% nos 15 min, rompimento em breakout_at e depois tendência `drift` por barra."""
    rng = random.Random(seed)
    closes = [round(base * k, 2) for k in (0.997, 1.004, 1.000)]
    p = base
    for i in range(3, N):
        if breakout_at is not None and i == breakout_at:
            p = base * 1.0075
        elif breakout_at is not None and i > breakout_at:
            p *= 1 + drift + rng.gauss(0, 0.0008)
        else:
            p = base * (1 + rng.uniform(-0.002, 0.002))
        closes.append(round(p, 2))
    return session(TODAY, closes, spread=base * 0.0008)


SCENARIOS = {
    "ACME": (history(1, 0.00015, 0.0015, 100.0), today_path(100.0, 4, 0.0007, 5)),
    "BRVO": (history(2, -0.0001, 0.0015, 50.0), today_path(50.0, 7, -0.0004, 6)),
    "CIRC": (history(3, 0.0, 0.0012, 200.0), today_path(200.0, None, 0.0, 7)),
}


class ReplayData:
    def sessions(self, symbol, now=None):
        past, today = SCENARIOS[symbol]
        days = OrderedDict(past)
        days[TODAY] = today
        return days


class ReplayBroker(PaperSim):
    """PaperSim que executa stop/alvo das brackets contra as barras do dia."""

    def __init__(self, cash):
        super().__init__(cash=cash)
        self.open, self.fills = {}, []

    def submit_bracket(self, symbol, qty, limit, stop, target, coid):
        res = super().submit_bracket(symbol, qty, limit, stop, target, coid)
        self.open[symbol] = {"qty": int(qty), "entry": limit, "stop": stop, "target": target}
        self.cash -= int(qty) * limit
        self.fills.append({"symbol": symbol, "side": "buy", "qty": int(qty), "price": limit})
        return res

    def on_bar(self, symbol, bar):
        pos = self.open.get(symbol)
        if not pos:
            return None
        px = pos["stop"] if bar["l"] <= pos["stop"] else pos["target"] if bar["h"] >= pos["target"] else None
        if px is None:
            return None
        return self._close(symbol, px, "stop" if px == pos["stop"] else "alvo")

    def _close(self, symbol, px, why):
        pos = self.open.pop(symbol)
        self.pos.pop(symbol, None)
        self.cash += pos["qty"] * px
        pnl = round(pos["qty"] * (px - pos["entry"]), 2)
        self.fills.append({"symbol": symbol, "side": "sell", "qty": pos["qty"], "price": px, "pnl": pnl, "why": why})
        return self.fills[-1]

    def account(self):
        a = super().account()
        eq = self.cash + sum(p["qty"] * p["entry"] for p in self.open.values())
        a.update(equity=str(eq), buying_power=str(self.cash))
        return a


def main(argv):
    cfg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "config.example.json")))
    cfg.update(mode="sim", watchlist=list(SCENARIOS), state_dir=tempfile.mkdtemp())
    cfg["timemachine"]["replays"] = 3000
    broker = ReplayBroker(cash=10000.0)
    journal = Journal(cfg["state_dir"])
    eng = Engine(cfg, broker, ReplayData(), journal, "sim")
    lines, seen = [], 0

    def say(t, kind, text):
        lines.append({"time": t, "kind": kind, "text": text})
        print("%s  %-6s %s" % (t, kind.upper(), text))

    say("09:25", "info", "trade-bot v0.1.1 · modo SIM · watchlist %s · capital US$ 10.000" % ", ".join(cfg["watchlist"]))
    for slot in range(1, N + 1):
        now_ny = datetime(TODAY.year, TODAY.month, TODAY.day, 9, 30, tzinfo=clock.NY) + timedelta(minutes=BM * slot)
        t = now_ny.strftime("%H:%M")
        for sym in list(broker.open):                         # executa stop/alvo da barra que acabou de fechar
            f = broker.on_bar(sym, SCENARIOS[sym][1][slot - 1])
            if f:
                say(t, "fill", "%s vendido %d @ %.2f (%s)  resultado %+.2f US$" % (sym, f["qty"], f["price"], f["why"], f["pnl"]))
        if slot == 3:
            say(t, "info", "faixa de abertura definida (09:30-09:45) para %d ativos" % len(SCENARIOS))
        status = eng.tick(now_ny.astimezone(timezone.utc))
        for ev in journal.read(TODAY.isoformat())[seen:]:
            seen += 1
            e = ev["event"]
            if e == "signal":
                say(t, "sinal", "%s rompeu a máxima %.2f · entrada %.2f · stop %.2f · alvo %.2f" % (
                    ev["symbol"], ev["or_high"], ev["entry"], ev["stop"], ev["target"]))
            elif e == "timemachine":
                verdict = "APROVADO" if ev["approved"] else "VETADO"
                say(t, "tm", "%s Máquina do Tempo (%d cenários, %d pregões): alvo %.0f%% · stop %.0f%% · vantagem %+.2f -> %s" % (
                    ev["symbol"], ev.get("replays", 0), ev.get("sessions", 0), 100 * ev.get("p_target", 0),
                    100 * ev.get("p_stop", 0), ev.get("edge", 0), verdict))
            elif e == "blocked":
                say(t, "risco", "%s bloqueado: %s" % (ev["symbol"], "; ".join(ev["reasons"])))
            elif e == "order":
                say(t, "ordem", "%s COMPRA %d @ %.2f · stop %.2f · alvo %.2f · risco máx US$ %.2f" % (
                    ev["symbol"], ev["qty"], ev["entry"], ev["stop"], ev["target"], ev["qty"] * (ev["entry"] - ev["stop"])))
            elif e == "flatten":
                say(t, "zerar", "zerando tudo (%s)" % ev["reason"])
        if status == "flat":
            break
    pnl = sum(f.get("pnl", 0) for f in broker.fills)
    say("16:00", "fim", "pregão encerrado · %d operação(ões) · resultado do dia %+.2f US$" % (
        sum(1 for f in broker.fills if f["side"] == "buy"), pnl))
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
        bars = {s: [[b["h"], b["l"], b["c"]] for b in SCENARIOS[s][1]] for s in SCENARIOS}
        json.dump({"lines": lines, "fills": broker.fills, "bars": bars, "pnl": pnl}, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
