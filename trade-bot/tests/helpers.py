"""Gera sessões sintéticas de 5 minutos (78 barras) para os testes offline."""

import random
import sys
import os
from collections import OrderedDict
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tradebot import clock  # noqa: E402

BM = 5
N = clock.session_slots(BM)


def bar_ts(d, slot):
    dt = datetime(d.year, d.month, d.day, 9, 30, tzinfo=clock.NY) + timedelta(minutes=BM * slot)
    return int(dt.timestamp())


def make_session(d, closes, spread=0.2):
    """Uma barra por fechamento; abre no fechamento anterior; máx/mín = ±spread."""
    out, prev = [], closes[0]
    for i, c in enumerate(closes):
        o = prev
        out.append({"t": bar_ts(d, i), "o": o, "h": max(o, c) + spread, "l": min(o, c) - spread, "c": c, "v": 1000})
        prev = c
    return out


def flat_then_breakout(d, base=100.0, breakout_slot=3, jump=1.0, after=None):
    """Faixa 99.8-100.2 nas 3 primeiras barras; rompe para cima em breakout_slot."""
    closes = [base] * N
    for i in range(breakout_slot, N):
        closes[i] = base + jump
    if after:
        for i, c in after.items():
            closes[i] = c
    return make_session(d, closes)


def random_sessions(n, seed=1, drift=0.0, start=date(2026, 7, 1), vol=0.002):
    rng = random.Random(seed)
    days, d = OrderedDict(), start
    while len(days) < n:
        if d.weekday() < 5:
            p, closes = 100.0, []
            for _ in range(N):
                p *= 1 + rng.gauss(drift, vol)
                closes.append(round(p, 2))
            days[d] = make_session(d, closes, spread=0.05)
        d += timedelta(days=1)
    return days


def cfg(**over):
    c = {
        "mode": "sim", "watchlist": ["TEST"], "bar_minutes": 5, "opening_range_minutes": 15,
        "stop_rule": "or_mid", "target_r": 1.0, "max_slippage_pct": 0.1,
        "no_entries_before": "09:45", "no_entries_after": "15:30", "flat_by": "15:55",
        "max_loss_per_trade_usd": 50, "max_daily_loss_usd": 150, "max_trades_per_day": 3,
        "max_open_positions": 2, "max_order_usd": 4000, "cash_buffer_pct": 10, "min_reward_risk": 1.0,
        "pdt_guard": True, "poll_seconds": 0,
        "timemachine": {"enabled": True, "replays": 500, "lookback_sessions": 59, "min_sessions": 20,
                        "seed": 19, "window": 2, "min_edge": 0.03, "min_avg_r": 0.0},
    }
    c.update(over)
    return c


def ny(d, hh, mm):
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=clock.NY)
