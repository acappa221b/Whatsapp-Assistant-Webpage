"""Diário em JSONL e estado do dia. REQ-10."""

import json
import os
from datetime import datetime, timezone


class Journal:
    def __init__(self, state_dir):
        self.dir = state_dir
        os.makedirs(state_dir, exist_ok=True)

    def path(self, day):
        return os.path.join(self.dir, "journal-%s.jsonl" % day)

    def log(self, day, event, **fields):
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": event, **fields}
        with open(self.path(day), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        return rec

    def read(self, day):
        p = self.path(day)
        if not os.path.exists(p):
            return []
        with open(p, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    # ---- estado do dia
    def _state_path(self, day):
        return os.path.join(self.dir, "day-%s.json" % day)

    def day_state(self, day):
        p = self._state_path(day)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        return {"traded": [], "trades": 0, "halted": False, "flattened": False}

    def save_day_state(self, day, st):
        tmp = self._state_path(day) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2)
        os.replace(tmp, self._state_path(day))

    # ---- kill switch (SEC-05)
    @property
    def kill_path(self):
        return os.path.join(self.dir, "KILL")

    def killed(self):
        return os.path.exists(self.kill_path)

    def set_kill(self, on):
        if on:
            open(self.kill_path, "w").close()
        elif self.killed():
            os.remove(self.kill_path)
