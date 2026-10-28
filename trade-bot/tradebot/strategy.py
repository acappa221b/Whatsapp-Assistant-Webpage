"""Opening Range Breakout (só compra). REQ-01, REQ-02, REQ-03."""


def opening_range(session, n_range):
    first = session[:n_range]
    if len(first) < n_range or any(b is None for b in first):
        return None
    return max(b["h"] for b in first), min(b["l"] for b in first)


def stop_price(rule, or_high, or_low):
    if rule == "or_low":
        return round(or_low - 0.01, 2)
    return round((or_high + or_low) / 2, 2)   # or_mid


def orb_signal(session, last_closed, cfg):
    """Avalia a sessão até o slot `last_closed` (inclusive).

    Retorna dict com status: waiting | triggered | expired | invalid | none.
    """
    bm = cfg.get("bar_minutes", 5)
    n = cfg.get("opening_range_minutes", 15) // bm
    if last_closed < n:
        return {"status": "waiting"}
    rng = opening_range(session, n)
    if rng is None:
        return {"status": "invalid", "reason": "faixa de abertura incompleta"}
    oh, ol = rng
    for i in range(n, last_closed + 1):
        b = session[i]
        if b is None:
            continue
        if b["c"] > oh:
            if i != last_closed:
                return {"status": "expired", "slot": i, "or_high": oh, "or_low": ol}
            entry = round(b["c"], 2)
            stop = stop_price(cfg.get("stop_rule", "or_mid"), oh, ol)
            risk = round(entry - stop, 2)
            if risk <= 0:
                return {"status": "invalid", "reason": "risco <= 0"}
            target = round(entry + cfg.get("target_r", 1.0) * risk, 2)
            return {"status": "triggered", "slot": i, "entry": entry, "stop": stop,
                    "target": target, "risk": risk, "or_high": oh, "or_low": ol}
    return {"status": "none", "or_high": oh, "or_low": ol}


def first_breakout(session, cfg, latest_slot):
    """Para o backtest: o primeiro rompimento até latest_slot, sem exigir frescor."""
    bm = cfg.get("bar_minutes", 5)
    n = cfg.get("opening_range_minutes", 15) // bm
    for i in range(n, latest_slot + 1):
        sig = orb_signal(session, i, cfg)
        if sig["status"] in ("triggered", "invalid"):
            return sig
        if sig["status"] == "expired":
            return None
    return None
