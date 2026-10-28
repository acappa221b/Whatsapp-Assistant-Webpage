#!/usr/bin/env bash
# Harness de liberação: tudo precisa passar antes de um merge/release.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== 1/5 versão consistente"
V="$(cat VERSION)"
grep -q "__version__ = \"$V\"" trade-bot/tradebot/__init__.py || { echo "VERSION ($V) != tradebot.__version__"; exit 1; }
grep -q "## \[$V\]" CHANGELOG.md || { echo "CHANGELOG sem a seção [$V]"; exit 1; }

echo "== 2/5 compilação"
python3 -m compileall -q trade-bot/tradebot trade-bot/tests

echo "== 3/5 testes unitários e de integração (offline)"
(cd trade-bot && python3 -m unittest discover -s tests)

echo "== 4/5 smoke test da CLI (modo sim, sem rede)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
python3 - "$TMP" <<'PY'
import json, sys
cfg = json.load(open("trade-bot/config.example.json"))
cfg.update(mode="sim", state_dir=sys.argv[1] + "/state")
json.dump(cfg, open(sys.argv[1] + "/config.json", "w"))
PY
(cd trade-bot && python3 -m tradebot --config "$TMP/config.json" kill on >/dev/null \
  && python3 -m tradebot --config "$TMP/config.json" tick | grep -qx killed \
  && python3 -m tradebot --config "$TMP/config.json" kill off >/dev/null)
python3 - "$TMP" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1] + "/config.json")); cfg["mode"] = "live"
json.dump(cfg, open(sys.argv[1] + "/live.json", "w"))
PY
if (cd trade-bot && env -u TRADEBOT_LIVE_CONFIRM python3 -m tradebot --config "$TMP/live.json" status 2>/dev/null); then
  echo "FALHA: modo live iniciou sem confirmação"; exit 1
fi

echo "== 5/5 skills vendorizadas têm licença"
for d in vendor/*/; do
  [ -d "$d" ] || continue
  ls "$d" | grep -qiE '^(LICENSE|LICENCE)' || { echo "sem LICENSE em $d"; exit 1; }
done

echo "HARNESS OK (v$V)"
