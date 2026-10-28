"""Máquina do Tempo: Monte Carlo por reamostragem das barras do mesmo horário. REQ-04, REQ-05.

Para cada slot i do pregão, o "pool" guarda os movimentos relativos (o, h, l, c)
divididos pelo fechamento da barra anterior em cada sessão passada completa.
Cada replay sorteia uma barra por slot (com janela ±window) e anda do slot k+1 até `last`.
"""

import random
import statistics

from .data import is_full


def build_pool(past_sessions):
    sessions = [s for s in past_sessions if is_full(s)]
    if not sessions:
        return [], 0
    n = len(sessions[0])
    pool = [[] for _ in range(n)]
    for s in sessions:
        for i in range(1, n):
            pc = s[i - 1]["c"]
            b = s[i]
            pool[i].append((b["o"] / pc, b["h"] / pc, b["l"] / pc, b["c"] / pc))
    return pool, len(sessions)


def simulate(pool, entry, stop, target, k, last, replays=5000, seed=19, window=2):
    n = len(pool)
    risk = entry - stop
    r_target = (target - entry) / risk
    rng = random.Random(seed)
    cnt = {"target": 0, "stop": 0, "close": 0}
    rs = []
    for _ in range(replays):
        p, outcome = entry, None
        for i in range(k + 1, last + 1):
            j = i if window == 0 else min(n - 1, max(1, i + rng.randint(-window, window)))
            _, h, l, c = rng.choice(pool[j])
            if p * l <= stop:
                outcome = "stop"          # stop e alvo na mesma barra: conta o stop
                break
            if p * h >= target:
                outcome = "target"
                break
            p = p * c
        outcome = outcome or "close"
        cnt[outcome] += 1
        rs.append(r_target if outcome == "target" else -1.0 if outcome == "stop" else (p - entry) / risk)
    return {
        "replays": replays, "seed": seed,
        "p_target": cnt["target"] / replays, "p_stop": cnt["stop"] / replays,
        "p_close": cnt["close"] / replays, "avg_r": statistics.mean(rs) if rs else 0.0,
        "r_target": r_target,
    }


def edge(mc):
    """Fatia do alvo entre os replays que bateram um lado, menos o ponto de equilíbrio 1/(1+R)."""
    hit = mc["p_target"] + mc["p_stop"]
    if hit <= 0:
        return 0.0
    return mc["p_target"] / hit - 1.0 / (1.0 + mc["r_target"])


def evaluate(past_sessions, signal, last_slot, tm_cfg):
    """Roda a simulação e decide. Retorna (aprovado: bool, relatório: dict)."""
    pool, n_sessions = build_pool(past_sessions)
    min_sessions = tm_cfg.get("min_sessions", 20)
    if n_sessions < min_sessions:
        return False, {"reason": "histórico insuficiente (%d < %d sessões)" % (n_sessions, min_sessions),
                       "sessions": n_sessions}
    mc = simulate(pool, signal["entry"], signal["stop"], signal["target"], signal["slot"], last_slot,
                  replays=tm_cfg.get("replays", 5000), seed=tm_cfg.get("seed", 19),
                  window=tm_cfg.get("window", 2))
    mc["edge"] = edge(mc)
    mc["sessions"] = n_sessions
    ok = mc["edge"] >= tm_cfg.get("min_edge", 0.03) and mc["avg_r"] >= tm_cfg.get("min_avg_r", 0.0)
    if not ok:
        mc["reason"] = "vantagem insuficiente (edge %.3f, R médio %.3f)" % (mc["edge"], mc["avg_r"])
    return ok, mc
