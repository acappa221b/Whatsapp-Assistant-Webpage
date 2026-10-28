# SPEC — trade-bot v0.1.0

Status: **Aprovada para implementação** · Dono: Alexandre Cappa · Última revisão: 2026-10-28

## 1. Objetivo

Robô de day trade **automático** para ações dos EUA via API da Alpaca. Ele
opera a estratégia de rompimento da faixa de abertura (Opening Range Breakout,
ORB) e filtra cada sinal com uma simulação Monte Carlo (a "Máquina do Tempo"),
inspirada no projeto open source `Jakeschincariol/day-trader-skill` (MIT).
Nenhum código foi copiado: a implementação é própria.

## 2. Fora de escopo (v0.1)

- B3 / MetaTrader 5, opções, venda a descoberto (short), margem, cripto.
- Varredura das ~6.000 ações dos EUA. A v0.1 opera uma **watchlist** definida no config.
- Interface gráfica. A operação é por linha de comando e por logs.

## 3. Requisitos funcionais

| ID | Requisito | Teste |
| --- | --- | --- |
| REQ-01 | Calcular a faixa de abertura (máxima e mínima das primeiras `opening_range_minutes`) a partir de barras de 5 minutos já **fechadas**. | `test_strategy` |
| REQ-02 | Sinal de compra só quando a barra fechada **mais recente** fecha acima da máxima da faixa (sinal fresco). Rompimento antigo = `expired`. | `test_strategy` |
| REQ-03 | Stop na metade da faixa (`or_mid`) ou na mínima (`or_low`). Alvo = entrada + `target_r` × risco. | `test_strategy` |
| REQ-04 | Máquina do Tempo: reamostra as barras do mesmo horário das sessões anteriores e simula o resto do dia N vezes (semente fixa, reproduzível). Se a barra tocar stop e alvo ao mesmo tempo, conta como **stop** (conservador). | `test_timemachine` |
| REQ-05 | Só opera se a vantagem medida (`edge`) ≥ `min_edge` **e** o R médio ≥ `min_avg_r`, com pelo menos `min_sessions` sessões de histórico. | `test_timemachine`, `test_engine` |
| REQ-06 | Quantidade = mínimo entre: `max_loss_per_trade_usd / risco`, `max_order_usd / preço` e `poder de compra × (1 − cash_buffer_pct)`. Zero = não opera. | `test_sizing` |
| REQ-07 | Regras de risco bloqueiam a ordem se: fora da janela de entrada, perda do dia ≥ limite, operações no dia ≥ limite, posições abertas ≥ limite, ativo já operado hoje, R:R < mínimo, regra PDT, ou kill switch ligado. | `test_risk` |
| REQ-08 | Toda entrada é uma ordem **bracket** (entrada limite + stop-loss + take-profit) com `client_order_id` único e determinístico (idempotente). | `test_broker` |
| REQ-09 | Zerar tudo (cancelar ordens e fechar posições) a partir de `flat_by`, ao atingir o limite de perda diária ou com o kill switch. | `test_engine` |
| REQ-10 | Toda decisão (sinal, bloqueio, ordem, erro) é gravada em `state/journal-AAAA-MM-DD.jsonl`. | `test_engine` |
| REQ-11 | Backtest walk-forward da mesma regra (com e sem o filtro da Máquina do Tempo), mostrando nº de trades, taxa de acerto, R médio, R total e drawdown máximo em R. | `test_backtest` |

## 4. Requisitos de segurança (obrigatórios)

| ID | Requisito | Teste |
| --- | --- | --- |
| SEC-01 | O modo padrão é `paper` (dinheiro fictício). | `test_broker` |
| SEC-02 | O modo `live` exige **as três** condições: `"mode": "live"` no config, a variável `TRADEBOT_LIVE_CONFIRM=I-ACCEPT-REAL-MONEY-RISK` e as chaves `ALPACA_LIVE_KEY_ID`/`ALPACA_LIVE_SECRET_KEY`. Faltando uma, o robô **não inicia**. | `test_broker` |
| SEC-03 | Chaves de API só por variável de ambiente, nunca no config nem nos logs. | `test_broker` |
| SEC-04 | No modo live, `max_daily_loss_usd` não pode passar de 5% do patrimônio, e `max_loss_per_trade_usd` não pode passar de 2%. Se passar, o robô não abre posições. | `test_risk` |
| SEC-05 | Kill switch: o arquivo `state/KILL` zera tudo e bloqueia novas entradas até ser removido. | `test_engine` |
| SEC-06 | Erro de rede ou de dados nunca abre posição. Na dúvida, o robô não opera. | `test_engine` |

## 5. Requisitos não funcionais

- Python ≥ 3.10, **só biblioteca padrão** (sem `pip install`).
- Testes 100% offline, com dados sintéticos e HTTP falso.
- Harness (`scripts/harness.sh`) roda compilação, testes e backtest de fumaça. É o portão de liberação (CI no GitHub Actions).
- Versionamento SemVer em `VERSION` e `CHANGELOG.md`.

## 6. Critérios de aceite para ligar o modo live

1. Harness verde.
2. No mínimo **20 pregões em paper** com o journal revisado.
3. Backtest com filtro da Máquina do Tempo com expectativa (R médio) > 0 na watchlist escolhida.
4. Limites do config revisados pelo dono.
