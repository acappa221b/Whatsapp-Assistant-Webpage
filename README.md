# claude-toolkit

Caixa de ferramentas para usar com o Claude Code, organizada com Spec Driven
Development, versionamento SemVer e um harness de testes que libera cada mudança.

| Pasta | O que é | Origem |
| --- | --- | --- |
| [`trade-bot/`](trade-bot/) | Robô de day trade automático (ações EUA via Alpaca): rompimento da faixa de abertura + Máquina do Tempo (Monte Carlo) + limites de risco | Código próprio, inspirado em `Jakeschincariol/day-trader-skill` (MIT) |
| [`vendor/marketingskills/`](vendor/marketingskills/) | 52 skills de marketing: CRO, copy, SEO, anúncios, cold e-mail, preços, lançamento… | coreyhaines31/marketingskills (MIT) |
| [`vendor/hyperframes/`](vendor/hyperframes/) | Skills do HyperFrames: o Claude escreve HTML e renderiza em vídeo MP4 | heygen-com/hyperframes (Apache-2.0) |
| [`vendor/brag/`](vendor/brag/) | `/brag`: transforma o site/app do projeto num vídeo de lançamento de 15-25 s (usa o HyperFrames) | latent-spaces/brag (MIT) |
| [`vendor/impeccable/`](vendor/impeccable/) | `/impeccable craft · audit · polish · typeset · animate…`: vocabulário de designer para tirar a "cara de IA" do site | pbakaus/impeccable (Apache-2.0) |
| [`vendor/taste-skill/`](vendor/taste-skill/) | Biblioteca de 202 sites premiados (Awwwards) descritos por estrutura, para o Claude copiar o padrão e não os pixels | Leonxlnx/taste-skill (MIT) |
| [`vendor/google-maps-scraper-kit/`](vendor/google-maps-scraper-kit/) | Extrai empresas do Google Maps localmente (Docker), operado pelo Claude · **leia o aviso legal** | Mahanaicoach (MIT) · [aviso](docs/leads-google-maps.md) |
| [`docs/leis-brasil.md`](docs/leis-brasil.md) | Todas as leis do Brasil em Markdown, baixando só as pastas que precisar | ctresb/leis (link + script) |
| [`docs/higgsfield.md`](docs/higgsfield.md) | Claude + Higgsfield (imagem/vídeo de produto) · **serviço pago** | Link oficial |
| [`vendor/awesome-design-md/`](vendor/awesome-design-md/) | 84 design systems (`DESIGN.md`) inspirados em marcas reais | VoltAgent/awesome-design-md (MIT) |
| [`docs/motion-graphics.md`](docs/motion-graphics.md) | Como fazer motion graphics com o Claude + galerias de prompts | Links (sem cópia de conteúdo) |

## Começo rápido

```bash
# 1. Garantir que está tudo verde
./scripts/harness.sh

# 2. Instalar as skills (marketing, vídeo, brag, design, taste) no Claude Code
./scripts/install-skills.sh                 # global (~/.claude/skills)
./scripts/install-skills.sh ../meu-projeto  # só num projeto

# 3. Dar a um projeto o visual de uma marca
./scripts/use-design.sh list
./scripts/use-design.sh linear.app ../meu-site

# 4. Leis do Brasil (só as pastas que precisar)
./scripts/leis.sh federal/leis-ordinarias   # a Constituição já vem junto

# 5. Robô de trade: ver trade-bot/README.md
```

## Processo (SDD + harness)

1. **Spec primeiro**: toda mudança começa na SPEC do módulo (ex.: `trade-bot/docs/SPEC.md`) com IDs de requisito.
2. **Decisões** em `docs/adr/` (por módulo).
3. **Testes** citam os IDs (REQ-xx, SEC-xx).
4. **Harness** (`scripts/harness.sh`): versão, compilação, testes, smoke da CLI e licenças. Roda no GitHub Actions a cada push/PR.
5. **Versão**: `VERSION` + `CHANGELOG.md` (SemVer). O harness falha se estiverem inconsistentes.
