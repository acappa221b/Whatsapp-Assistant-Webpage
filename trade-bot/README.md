# trade-bot

Robô de day trade **automático** para ações dos EUA na Alpaca. Requisitos em
[`docs/SPEC.md`](docs/SPEC.md) e decisões em [`docs/adr/`](docs/adr/).

> ⚠️ **Risco real.** Day trade dá prejuízo para a maioria das pessoas físicas.
> Este robô não garante lucro. A simulação usa o passado, e o passado não se
> repete. Só use dinheiro que você aceita perder.

## Como ele opera (a cada minuto, durante o pregão)

1. **Sinal**: para cada ativo da watchlist, calcula a faixa dos primeiros 15 min. Quando uma barra de 5 min **acaba de fechar** acima da máxima, gera um sinal de compra.
2. **Plano**: stop na metade da faixa e alvo de 1R (configurável).
3. **Máquina do Tempo**: simula o resto do pregão 5.000 vezes com as barras do mesmo horário dos últimos 59 pregões. Só segue se a vantagem for positiva.
4. **Tamanho**: quantidade para perder no máximo `max_loss_per_trade_usd` no stop.
5. **Risco**: janela de horário, perda do dia, nº de operações, posições abertas, regra PDT e kill switch.
6. **Ordem**: bracket na Alpaca (entrada limite + stop + alvo, tudo na corretora). Se o robô cair, o stop continua valendo.
7. **15:55 ET**: cancela tudo e zera as posições.

Tudo fica registrado em `state/journal-AAAA-MM-DD.jsonl`.

## Instalação

Só precisa de Python ≥ 3.10, sem `pip install`.

```bash
cd trade-bot
cp config.example.json config.json      # edite watchlist e limites
```

Crie uma conta na [Alpaca](https://alpaca.markets) e gere as chaves **paper**:

```bash
export ALPACA_PAPER_KEY_ID=...
export ALPACA_PAPER_SECRET_KEY=...
```

## Uso

```bash
python3 -m tradebot backtest            # testa a regra nos últimos ~60 dias
python3 -m tradebot status              # conta e estado do dia
python3 -m tradebot run                 # liga o robô (Ctrl+C para parar)
python3 -m tradebot kill on             # EMERGÊNCIA: zera tudo e bloqueia entradas
python3 -m tradebot kill off
python3 -m tradebot flatten             # zera agora
```

Modos (`"mode"` no config):

| modo | o que faz |
| --- | --- |
| `sim` | corretora fictícia em memória, sem chave (para testar o fluxo) |
| `paper` | **padrão**. Conta simulada da Alpaca, com dados e execução reais e dinheiro fictício |
| `live` | **dinheiro real** |

## Ligando o modo live (dinheiro real)

Siga os critérios da SPEC §6 (no mínimo 20 pregões em paper). Depois, **as três** condições abaixo:

```bash
# 1. config.json -> "mode": "live"
# 2. chaves LIVE (separadas das paper)
export ALPACA_LIVE_KEY_ID=...
export ALPACA_LIVE_SECRET_KEY=...
# 3. confirmação explícita
export TRADEBOT_LIVE_CONFIRM=I-ACCEPT-REAL-MONEY-RISK
python3 -m tradebot run
```

No modo live, o robô também se recusa a abrir posições se a perda diária
configurada passar de 5% do patrimônio ou a perda por operação passar de 2%.

Para rodar o dia todo sem o computador ligado, use um servidor barato
(ex.: uma VM Linux) com `tmux` ou `systemd`, no fuso de Nova York.

## Limitações conhecidas (v0.1)

- Só compra (sem short), só ações dos EUA e só a watchlist (sem varrer o mercado todo).
- Dados gratuitos da Alpaca (feed IEX) cobrem uma parte do volume. A ordem limite com 0,1% de tolerância evita pagar caro demais, mas pode não ser executada.
- Contas abaixo de US$25 mil caem na regra PDT: no máximo 3 day trades em 5 dias úteis.
- A Máquina do Tempo assume que o comportamento intradiário recente se repete. Notícias e resultados trimestrais quebram essa premissa.
