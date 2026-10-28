#!/usr/bin/env bash
# Instala as skills no Claude Code.
#   ./scripts/install-skills.sh            -> ~/.claude/skills (todas as conversas)
#   ./scripts/install-skills.sh <projeto>  -> <projeto>/.claude/skills
#   PACKS="marketing video brag" ./scripts/install-skills.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:+$1/.claude/skills}"; DEST="${DEST:-$HOME/.claude/skills}"
PACKS="${PACKS:-marketing video brag}"
mkdir -p "$DEST"
for p in $PACKS; do
  case "$p" in
    marketing) SRC="$ROOT/vendor/marketingskills/skills" ;;
    video)     SRC="$ROOT/vendor/hyperframes/skills" ;;
    brag)      SRC="$ROOT/vendor/brag/skills" ;;
    *) echo "pack desconhecido: $p (use marketing, video, brag)"; exit 1 ;;
  esac
  for d in "$SRC"/*/; do cp -r "$d" "$DEST/"; echo "  + $(basename "$d")"; done
done
echo "Skills instaladas em $DEST"
