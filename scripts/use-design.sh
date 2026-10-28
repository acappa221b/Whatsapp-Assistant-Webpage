#!/usr/bin/env bash
# Copia o DESIGN.md de uma marca para a raiz de um projeto e referencia no CLAUDE.md.
#   ./scripts/use-design.sh list
#   ./scripts/use-design.sh stripe ../meu-site
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; LIB="$ROOT/vendor/awesome-design-md/design-md"
if [ "${1:-list}" = "list" ]; then ls "$LIB"; exit 0; fi
SLUG="$1"; TARGET="${2:-.}"
[ -f "$LIB/$SLUG/DESIGN.md" ] || { echo "marca não encontrada: $SLUG (veja: $0 list)"; exit 1; }
cp "$LIB/$SLUG/DESIGN.md" "$TARGET/DESIGN.md"
LINE="Siga o DESIGN.md na raiz para cores, tipografia, espaçamento e componentes de UI."
grep -qsF "$LINE" "$TARGET/CLAUDE.md" || printf '\n%s\n' "$LINE" >> "$TARGET/CLAUDE.md"
echo "DESIGN.md ($SLUG) copiado para $TARGET e referenciado no CLAUDE.md"
