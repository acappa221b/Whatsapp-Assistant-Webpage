#!/usr/bin/env bash
# Reimporta as skills de terceiros a partir do GitHub (não executa nada delas).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fetch() { git clone -q --depth 1 "https://github.com/$1.git" "$TMP/$2"; echo "$2 -> $(git -C "$TMP/$2" rev-parse --short=12 HEAD)"; }
fetch coreyhaines31/marketingskills marketingskills
fetch heygen-com/hyperframes hyperframes
fetch VoltAgent/awesome-design-md awesome-design-md
rm -rf "$ROOT/vendor/marketingskills" "$ROOT/vendor/hyperframes" "$ROOT/vendor/awesome-design-md"
mkdir -p "$ROOT/vendor/marketingskills" "$ROOT/vendor/hyperframes" "$ROOT/vendor/awesome-design-md"
cp -r "$TMP/marketingskills/"{skills,LICENSE,README.md} "$ROOT/vendor/marketingskills/"
cp -r "$TMP/hyperframes/"{skills,LICENSE} "$ROOT/vendor/hyperframes/"
cp -r "$TMP/awesome-design-md/"{design-md,LICENSE,README.md} "$ROOT/vendor/awesome-design-md/"
echo "Atualize vendor/SOURCES.md e o CHANGELOG com os commits acima, depois rode scripts/harness.sh"
