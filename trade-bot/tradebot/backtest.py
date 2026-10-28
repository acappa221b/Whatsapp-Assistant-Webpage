"""Backtest walk-forward da regra ORB, com e sem a Máquina do Tempo. REQ-11."""

from . import clock, strategy, timemachine
from .data import is_full


def play_out(session, sig, last_slot):
    """Resultado real da operação: R obtido. Stop e alvo na mesma barra = stop."""
    risk = sig["entry"] - sig["stop"]
    for i in range(sig["slot"] + 1, last_slot + 1):
        b = session[i]
        if b is None:
            continue
        if b["l"] <= sig["stop"]:
            return -1.0, "stop"
        if b["h"] >= sig["target"]:
            return (sig["target"] - sig["entry"]) / risk, "target"
    last = next((session[i] for i in range(last_slot, -1, -1) if session[i] is not None), None)
    return (last["c"] - sig["entry"]) / risk, "close"


def run(sessions, cfg, use_timemachine=True):
    """sessions: OrderedDict data -> sessão. Usa só sessões anteriores para a simulação."""
    bm = cfg.get("bar_minutes", 5)
    last_slot = clock.slot_ending_at(cfg["flat_by"], bm)
    latest_entry = clock.slot_ending_at(cfg["no_entries_after"], bm)
    tm_cfg = cfg.get("timemachine", {})
    lookback = tm_cfg.get("lookback_sessions", 59)
    days = list(sessions.items())
    trades = []
    for idx, (d, s) in enumerate(days):
        if not is_full(s):
            continue
        sig = strategy.first_breakout(s, cfg, latest_entry)
        if not sig or sig.get("status") != "triggered":
            continue
        past = [x for _, x in days[max(0, idx - lookback):idx]]
        if use_timemachine:
            ok, _ = timemachine.evaluate(past, sig, last_slot, tm_cfg)
            if not ok:
                continue
        r, how = play_out(s, sig, last_slot)
        trades.append({"date": d.isoformat(), "r": round(r, 3), "outcome": how,
                       "entry": sig["entry"], "stop": sig["stop"], "target": sig["target"]})
    return summarize(trades)


def summarize(trades):
    rs = [t["r"] for t in trades]
    eq = peak = dd = 0.0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    n = len(rs)
    return {"trades": n, "win_rate": (sum(1 for r in rs if r > 0) / n) if n else 0.0,
            "avg_r": (sum(rs) / n) if n else 0.0, "total_r": sum(rs), "max_dd_r": dd, "list": trades}
