"""Regras de risco: devolvem a lista de motivos de bloqueio (vazia = PASS). REQ-07, SEC-04."""

from . import clock

LIVE_MAX_DAILY_LOSS_PCT = 0.05
LIVE_MAX_TRADE_LOSS_PCT = 0.02
PDT_EQUITY = 25000.0


def check_entry(order, ctx, cfg):
    """order: symbol, qty, entry, stop, target. ctx: estado atual (ver engine)."""
    reasons = []
    m = clock.minute_of_day(ctx["now_ny"])
    if m < clock.hhmm_to_min(cfg["no_entries_before"]) or m > clock.hhmm_to_min(cfg["no_entries_after"]):
        reasons.append("fora da janela de entrada")
    if ctx.get("killed"):
        reasons.append("kill switch ligado")
    if ctx.get("halted"):
        reasons.append("robô parado hoje (limite de perda diária)")
    if ctx["day_pnl"] <= -cfg["max_daily_loss_usd"]:
        reasons.append("perda do dia %.2f atingiu o limite" % ctx["day_pnl"])
    if ctx["trades_today"] >= cfg["max_trades_per_day"]:
        reasons.append("limite de operações do dia")
    if ctx["open_positions"] >= cfg["max_open_positions"]:
        reasons.append("limite de posições abertas")
    if order["symbol"] in ctx["traded_symbols"] or order["symbol"] in ctx.get("held_symbols", ()):
        reasons.append("%s já operado hoje" % order["symbol"])
    if order["qty"] < 1:
        reasons.append("quantidade zero")
    risk = order["entry"] - order["stop"]
    if risk <= 0:
        reasons.append("stop acima da entrada")
    elif (order["target"] - order["entry"]) / risk < cfg.get("min_reward_risk", 1.0) - 1e-9:
        reasons.append("retorno/risco abaixo do mínimo")
    elif order["qty"] * risk > cfg["max_loss_per_trade_usd"] + 0.01:
        reasons.append("perda no stop acima do máximo por operação")
    equity = ctx["equity"]
    if cfg.get("pdt_guard", True) and equity < PDT_EQUITY and ctx.get("daytrade_count", 0) >= 3:
        reasons.append("regra PDT: 3 day trades em 5 dias com patrimônio < US$25 mil")
    if ctx["mode"] == "live":
        if cfg["max_daily_loss_usd"] > equity * LIVE_MAX_DAILY_LOSS_PCT:
            reasons.append("config: perda diária máxima > 5% do patrimônio")
        if cfg["max_loss_per_trade_usd"] > equity * LIVE_MAX_TRADE_LOSS_PCT:
            reasons.append("config: perda por operação > 2% do patrimônio")
    return reasons
