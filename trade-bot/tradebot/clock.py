"""Horário de Nova York e slots de barras do pregão regular (09:30-16:00 ET)."""

from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
OPEN_MIN = 9 * 60 + 30   # 09:30
CLOSE_MIN = 16 * 60      # 16:00


def to_ny(ts: float) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(NY)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def hhmm_to_min(text: str) -> int:
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def minute_of_day(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


def session_slots(bar_minutes: int) -> int:
    return (CLOSE_MIN - OPEN_MIN) // bar_minutes


def slot_of(dt_ny: datetime, bar_minutes: int):
    """Índice da barra que COMEÇA em dt_ny; None fora do pregão regular."""
    m = minute_of_day(dt_ny)
    if m < OPEN_MIN or m >= CLOSE_MIN:
        return None
    return (m - OPEN_MIN) // bar_minutes


def last_closed_slot(now_ny: datetime, bar_minutes: int) -> int:
    """Índice da última barra totalmente fechada em now_ny (-1 se nenhuma)."""
    m = minute_of_day(now_ny)
    if m < OPEN_MIN:
        return -1
    m = min(m, CLOSE_MIN)
    return (m - OPEN_MIN) // bar_minutes - 1


def slot_ending_at(hhmm: str, bar_minutes: int) -> int:
    """Índice da barra que termina no horário dado (ex.: 15:55 com 5 min -> 76)."""
    return (hhmm_to_min(hhmm) - OPEN_MIN) // bar_minutes - 1


def ny_date(dt: datetime) -> date:
    return dt.astimezone(NY).date()
