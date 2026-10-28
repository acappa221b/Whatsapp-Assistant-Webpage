# Regras para o Claude neste repositório

- Spec Driven Development: altere a SPEC do módulo **antes** do código; cada requisito tem ID (REQ-xx/SEC-xx) e um teste que o cita.
- Rode `./scripts/harness.sh` antes de cada commit. Só faça merge com o harness verde.
- Toda release atualiza `VERSION`, `trade-bot/tradebot/__init__.py` e `CHANGELOG.md`.
- `vendor/` é cópia fiel de terceiros: não editar. Atualize com `scripts/update-vendor.sh`.
- trade-bot: nunca enfraqueça os requisitos SEC-xx (modo live, limites, kill switch) sem uma ADR nova aprovada pelo dono.
- Chaves de API nunca entram no repositório (use variáveis de ambiente / `.env`, que é ignorado).
