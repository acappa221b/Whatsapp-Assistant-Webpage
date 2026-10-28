# Código de terceiros (vendor)

Cópias **sem alteração** de projetos open source, com as licenças originais
mantidas em cada pasta. Para atualizar, use `scripts/update-vendor.sh` e
registre o novo commit aqui e no CHANGELOG.

| Pasta | Origem | Licença | Commit | Data |
| --- | --- | --- | --- | --- |
| `marketingskills/` | https://github.com/coreyhaines31/marketingskills (Corey Haines) | MIT | `0cd9b3a0ef4c` | 2026-10-27 |
| `hyperframes/` (só `skills/`) | https://github.com/heygen-com/hyperframes (HeyGen) | Apache-2.0 | `439d6856780f` | 2026-10-27 |
| `brag/` (só `skills/` + README) | https://github.com/latent-spaces/brag (Shunit Haviv Hakimi) | MIT (código) · músicas CC BY 4.0 (Sascha Ende) · SFX Kenney (CC0) | `669ab9286aa2` | 2026-10-24 |
| `awesome-design-md/` | https://github.com/VoltAgent/awesome-design-md (VoltAgent) | MIT | `3b605329240c` | 2026-10-14 |

## Avisos

- **HyperFrames**: só as skills foram copiadas. A renderização de vídeo usa a CLI
  oficial pelo npm (`npx hyperframes ...`), que exige Node ≥ 22 e FFmpeg.
- **brag**: as músicas exigem crédito ao publicar o vídeo: "Music: Sascha Ende, ende.app (CC BY 4.0)". Use `--no-music` para dispensar.
- **DESIGN.md de marcas**: são análises "inspiradas" em sites públicos, para
  estudo e protótipos internos. Logos, nomes e a identidade visual pertencem às
  marcas. Não publique um produto que copie a marca de outra empresa.
- Não foram executados scripts desses projetos durante a importação.
