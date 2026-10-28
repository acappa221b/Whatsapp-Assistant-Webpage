#!/usr/bin/env bash
# Reimporta as skills de terceiros a partir do GitHub (não executa nada delas).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fetch() { git clone -q --depth 1 "https://github.com/$1.git" "$TMP/$2"; echo "$2 -> $(git -C "$TMP/$2" rev-parse --short=12 HEAD)"; }
fetch coreyhaines31/marketingskills marketingskills
fetch heygen-com/hyperframes hyperframes
fetch VoltAgent/awesome-design-md awesome-design-md
fetch latent-spaces/brag brag
fetch pbakaus/impeccable impeccable
fetch Leonxlnx/taste-skill taste-skill
fetch Mahanaicoach/google-maps-scraper-kit google-maps-scraper-kit
rm -rf "$ROOT/vendor/marketingskills" "$ROOT/vendor/hyperframes" "$ROOT/vendor/awesome-design-md" "$ROOT/vendor/brag" "$ROOT/vendor/impeccable" "$ROOT/vendor/taste-skill" "$ROOT/vendor/google-maps-scraper-kit"
mkdir -p "$ROOT/vendor/marketingskills" "$ROOT/vendor/hyperframes" "$ROOT/vendor/awesome-design-md" "$ROOT/vendor/brag" "$ROOT/vendor/impeccable" "$ROOT/vendor/taste-skill" "$ROOT/vendor/google-maps-scraper-kit"
cp -r "$TMP/marketingskills/"{skills,LICENSE,README.md} "$ROOT/vendor/marketingskills/"
cp -r "$TMP/hyperframes/"{skills,LICENSE} "$ROOT/vendor/hyperframes/"
cp -r "$TMP/awesome-design-md/"{design-md,LICENSE,README.md} "$ROOT/vendor/awesome-design-md/"
cp -r "$TMP/brag/"{skills,LICENSE,README.md} "$ROOT/vendor/brag/"
cp -r "$TMP/impeccable/"{plugin,LICENSE,NOTICE.md,README.md} "$ROOT/vendor/impeccable/"
cp -r "$TMP/taste-skill/"{skills,LICENSE,README.md} "$ROOT/vendor/taste-skill/"
(cd "$TMP/google-maps-scraper-kit" && tar --exclude=.git -cf - .) | (cd "$ROOT/vendor/google-maps-scraper-kit" && tar xf -)
echo "Atualize vendor/SOURCES.md e o CHANGELOG com os commits acima, depois rode scripts/harness.sh"
