"""Tamanho da posição. REQ-06."""

import math


def position_size(entry, stop, buying_power, cfg):
    risk = entry - stop
    if risk <= 0 or entry <= 0:
        return 0
    by_loss = cfg["max_loss_per_trade_usd"] / risk
    by_order = cfg["max_order_usd"] / entry
    by_cash = max(0.0, buying_power) * (1 - cfg.get("cash_buffer_pct", 10) / 100.0) / entry
    return max(0, math.floor(min(by_loss, by_order, by_cash)))
