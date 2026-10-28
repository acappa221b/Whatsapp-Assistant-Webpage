#!/usr/bin/env bash
# Baixa só as pastas pedidas do repositório ctresb/leis (sparse checkout).
#   ./scripts/leis.sh federal/leis-ordinarias      (constituicao.md e os arquivos da raiz já vêm sempre)
set -euo pipefail
DEST="${LEIS_DIR:-$HOME/leis}"
[ $# -gt 0 ] || { echo "uso: $0 <pasta-ou-arquivo> [...]  (ex.: federal/leis-ordinarias constituicao.md)"; exit 1; }
if [ ! -d "$DEST/.git" ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/ctresb/leis.git "$DEST"
fi
# arquivos da raiz (ex.: constituicao.md) já vêm sempre; só pastas entram no sparse checkout
DIRS=()
for a in "$@"; do
  case "$a" in */*|[!.]*) [[ "$a" == */* || ! "$a" =~ \.[a-z]+$ ]] && DIRS+=("${a%/}") ;; esac
done
[ ${#DIRS[@]} -eq 0 ] || git -C "$DEST" sparse-checkout add "${DIRS[@]}"
echo "Pronto em $DEST: $(find "$DEST" -name '*.md' -not -path '*/.git/*' | wc -l) arquivos .md"
